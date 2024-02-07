
import time
import os
import sys
import Shell
from Base import Base, Opt
from Json import Json
import Log

web={
  "kanxig":{
    "name":"看戏网",
    "url":["https://www.kanxig.com/"],
    "search":"search/-------------.html?wd=",
    "res_tag": "var player_data"
  }
}

class Movie(Base):
    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.__args_list = args_list or []
        self.option_dic = {
            "search": self.search,
            "sync": self.sync,
            "download": self.download,
            "show": self.show,
        }
        
        self.web_dic = self.config.read(web)
        Log.debug(self.web_dic)
        

    # 子命令方法
    def search(self, arg: list):
        Log.todo()
        LOg.debug()

    def sync(self, arg: list):
        Log.todo()

    def download(self, arg: list):
        Log.todo()

    def show(self, arg: list):
        Log.todo()

    def help(self):
        Log.tips("请输入 %s movie [option]" % (self.tool_name))
        Log.tips("[option]: %s" % (" | ".join(self._opt().get_sub_opt())))

    # 子命令补全提示方法
    def _opt(self):
        return Opt(list(self.option_dic.keys()))

    def sync_opt(self):
        return Opt([])

    def show_opt(self):
        return Opt([])

    # 执行方法
    def exec(self):
        if len(self.__args_list) < 1:
            self.help()
        else:
            self.option_dic[self.__args_list[0]](self.__args_list[1:])
