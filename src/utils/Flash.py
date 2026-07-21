from Shell import Shell
from Base import Base
import Log

import os
import json


class Flash(Base):
    def __init__(self, args=None):
        super().__init__(args)
        self.meta("根据工程配置选择设备和镜像并执行烧录命令。", args="[选项]")
        self.flash_dic = {}
        self.project_top_dir = self.find_project_top_dir()
          
        if self.project_top_dir:
            build_dic = {}
            if os.path.exists(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")):
                with open(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")) as f:
                    build_dic.update(json.load(f))
                    self.flash_dic = build_dic["flash_tool"]



        self.devices_cmd = {
            "uart": self.find_uart_devices,
        }

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
        if self.should_show_help(self.args):
            self.help()
            return
        try:
            cmd = self.handle_cmd()
            if cmd:
                Shell.bash(cmd).status()
        except Exception as e:
            Log.error(e)
