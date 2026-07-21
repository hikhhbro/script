from turtle import update
from Shell import Shell
from Base import Base, Opt
import Log

import os
import re
import pathlib
import json
try:
    import xmltodict
except ImportError:
    xmltodict = None
import time
import itertools
from datetime import datetime, timedelta



def components(path):
    '''
    返回路径的各级组成部分。

    返回结果重新用 os.path.join 拼接后，仍指向原路径位置。
    '''
    components = []
    # 循环保证拆出的路径片段重新拼接后仍指向同一位置。
    # os.path.joined with the path separator and point to the same
    # location:    
    while True:
        (new_path, tail) = os.path.split(path)  # 兼容不同平台
        components.append(tail)        
        if new_path == path:  # 已到达根目录
            break
        path = new_path
    components.append(new_path)

    components.reverse()  # 保持从根到叶子的顺序
    return components

def longest_prefix(iter0, iter1):
    '''
    返回两个可迭代对象的最长公共前缀。
    '''
    longest_prefix = []
    for (elmt0, elmt1) in zip(iter0, iter1):
        if elmt0 != elmt1:
            break
        longest_prefix.append(elmt0)
    return longest_prefix

def common_prefix_path(path0, path1):
    return os.path.join(*longest_prefix(components(path0), components(path1)))

class Flash(Base):
    help_summary = "根据工程配置选择设备和镜像并执行烧录命令。"
    help_usage = "{tool_name} flash [选项]"
    help_options = {
        "--help": "显示当前帮助",
    }
    help_examples = [
        "hikrun flash",
    ]

    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.__args_list = self.args
        self.flash_dic = {}
        self.projects_path = self.tool_dir + '/data/build/projects_dir'
        self.projects_list = []

        if not os.path.exists(self.tool_dir + '/data/build'):
            os.makedirs(self.tool_dir + '/data/build', exist_ok=True)
        if os.path.exists(self.projects_path):
            with open(self.projects_path) as f:
                self.projects_list = json.load(f)
        self.cur_dir = os.getcwd() + '/'
        self.project_top_dir = self.__get_project_top_dir()
          
        if self.project_top_dir:
            build_dic = {}
            if os.path.exists(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")):
                with open(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")) as f:
                    build_dic.update(json.load(f))
                    self.flash_dic = build_dic["flash_tool"]



        self.devices_cmd = {
            "uart": self.find_uart_devices,
        }




    def __get_project_top_dir(self):
      Log.debug("获取工程顶级目录")
      # max_len = 0
      # top_dir = ""
      Log.debug(self.projects_list)
      Log.debug(self.cur_dir)
      for item in self.projects_list:
          prefix = common_prefix_path(self.cur_dir,item)
          Log.debug(prefix)
          if prefix in self.projects_list :
              return prefix
      return None


    # def handle_cmd(self):
    #   Log.debug(self.__args_list)
    #   if len(self.__args_list) > 1 and  "-p" in self.__args_list[0]:
    #     if "port" in self.flash_dic.keys():
    #       self.flash_dic["port"] = "/dev/ttyUSB%s" %(self.__args_list[1])
    #   else :
    #     self.flash_dic["port"] = self.find_devices(self.flash_dic["port"])
    #   str = ""
    #   for key,value in self.flash_dic.items():
    #     # if key == "tool": 
    #     #     str = "sudo " + value + " "
    #     Log.debug(value)
    #     Log.debug(key)
    #     str += ("sudo " + value + " ") if key == "tool"  else  (" --" + key + "=" + value + " ")
    #   Log.debug(str)
    #   return str


    def is_devices(self, key):
      if self.devices_cmd.__contains__(key):
          return  self.devices_cmd[key]
      return  ""

    def find_uart_devices(self):
      devices = []
      datanames = os.listdir("/dev")  
      for i in datanames:
        if "ttyUSB" in i or  "ttyCH" in i:
          devices.append("/dev/" + i)
      devices.sort()
      Log.debug(devices)
      if not devices:
          return ''
      ret = devices[0]
      if len(devices) > 1:
          for i in range(len(devices)):
            Log.tips("%d:%s" % (i, devices[i]))
          ret = Log.getcmd("选择窗口设备", devices[0] +  " or 0")
          Log.debug(ret)
          if ret.isdigit():
              ret = devices[int(ret)]
          Log.debug(ret)
      return ret
    

  
    def get_arg_value(self,arg):
      if isinstance(self.flash_dic[arg],str):
        if self.is_devices(self.flash_dic[arg]):
            return self.devices_cmd[self.flash_dic[arg]]()
      elif isinstance(self.flash_dic[arg],dict):
        if len(list(self.flash_dic[arg].values())) == 1: 
          return list(self.flash_dic[arg].values())[0]
      
        key = Log.select("请选择烧录镜像",list(self.flash_dic[arg].keys()))
        Log.debug(key)
        return self.flash_dic[arg][key]


    def handle_cmd(self):
      cmd_list = self.flash_dic['cmd'].split(' ')
      for i  in range(0,len(cmd_list)):
        if '$' == cmd_list[i][0]:
          cmd_list[i] = self.get_arg_value(cmd_list[i])
          
        elif '=$' in cmd_list[i]:
          start = cmd_list[i].rfind('$')
          cmd_list[i] = cmd_list[i][0:start] + self.get_arg_value(cmd_list[i][start:])

      Log.debug(cmd_list)
      return ' '.join(cmd_list)
          
      Log.debug(cmd_list)

    def exec(self):
        if self.should_show_help(self.__args_list):
            self.help()
            return
        try:
            cmd = self.handle_cmd()
            if cmd:
                Shell.bash(cmd).status()
        except Exception as e:
            Log.error(e)

    def help(self, command=None):
        super().help(command)

    def _opt(self):
        return Opt([])




    # def _opt(self):
    #     if self.cur[0] == '-':
    #         return list(self.option_dic.keys())
    #     return ["get_file_opt"] + self.__get_history()
