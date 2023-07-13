from turtle import update
from command.Shell import Shell
from command.Base import Base
from command.Log import Log

import os
import re
import pathlib
import json
import xmltodict
import time
import itertools
from datetime import datetime, timedelta



def components(path):
    '''
    Returns the individual components of the given file path
    string (for the local operating system).

    The returned components, when joined with os.path.join(), point to
    the same location as the original path.
    '''
    components = []
    # The loop guarantees that the returned components can be
    # os.path.joined with the path separator and point to the same
    # location:    
    while True:
        (new_path, tail) = os.path.split(path)  # Works on any platform
        components.append(tail)        
        if new_path == path:  # Root (including drive, on Windows) reached
            break
        path = new_path
    components.append(new_path)

    components.reverse()  # First component first
    return components

def longest_prefix(iter0, iter1):
    '''
    Returns the longest common prefix of the given two iterables.
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
    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.__args_list = args_list or ['']
        self.flash_dic = {}
        self.projects_path = self.tool_dir + '/data/build/projects_dir'
        
        if not os.path.exists(self.tool_dir + '/data/build'):
            Shell('mkdir -p ' + self.tool_dir + '/data/build').exec_system()
        if os.path.exists(self.projects_path):
            with open(self.projects_path) as f:
                self.projects_list = json.load(f)
        self.cur_dir = os.getcwd() + '/'
        self.project_top_dir = self.__get_project_top_dir() 
        self.projects_list = []      
          
        if self.project_top_dir:
            build_dic = {}
            if os.path.exists(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")):
                with open(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")) as f:
                    build_dic.update(json.load(f))
                    self.flash_dic = build_dic["flash_tool"]



        # self.build_cmd = {
        #     "monking": self.monking,
        #     "aosp": self.aosp,
        #     "vela": self.vela,
        #     "flutter": " ",
        #     "buildroot": " ",
        # }




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


    def handle_cmd(self):
      Log.debug(self.__args_list)
      if len(self.__args_list) > 1 and  "-p" in self.__args_list[0]:
        if "port" in self.flash_dic.keys():
          self.flash_dic["port"] = "/dev/ttyUSB%s" %(self.__args_list[1])
      else :
        self.flash_dic["port"] = self.find_devices(self.flash_dic["port"])
      str = ""
      for key,value in self.flash_dic.items():
        # if key == "tool": 
        #     str = "sudo " + value + " "
        Log.debug(value)
        Log.debug(key)
        str += ("sudo " + value + " ") if key == "tool"  else  (" --" + key + "=" + value + " ")
      Log.debug(str)
      return str

    def find_devices(self,device):
      devices = []
      if "/dev/ttyUSB" in  device:
        datanames = os.listdir("/dev")  
        for i in datanames:
          if "ttyUSB" in i:
            devices.append("/dev/" + i)
      Log.debug(devices)
      if len(devices) > 1:
          for i in range(len(devices)):
            Log.tips("%d:%s" % (i, devices[i]))
          ret = Log.input("选择窗口设备", devices[0] +  " or 0")
          Log.debug(ret)
          if ret.isdigit():
              ret = devices[int(ret)]
          Log.debug(ret)
      return ret
          

    def exec(self):
        try:
          Shell(self.handle_cmd())
        except Exception as e:
            Log.error(e)

    def help(self, arg: list):
        pass




    # def _opt(self):
    #     if self.cur[0] == '-':
    #         return list(self.option_dic.keys())
    #     return ["get_file_opt"] + self.__get_history()