
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
    help_summary = "影视搜索、同步和下载入口。"
    help_usage = "{tool_name} movie <子命令> [参数]"
    help_options = {
        "search": "搜索影视资源",
        "sync": "同步影视数据",
        "download": "下载影视资源",
        "show": "展示已记录资源",
        "--help": "显示当前帮助",
    }
    help_examples = [
        "hikrun movie search 电影名",
        "hikrun movie show",
    ]

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
        Log.debug("movie search is not implemented")

    def sync(self, arg: list):
        Log.todo()

    def download(self, arg: list):
        Log.todo()

    def show(self, arg: list):
        Log.todo()

    def help(self, command=None):
        super().help(command)

    # 子命令补全提示方法
    def _opt(self):
        return Opt(list(self.option_dic.keys()))

    def sync_opt(self):
        return Opt([])

    def show_opt(self):
        return Opt([])

    # 执行方法
    def exec(self):
        if self.should_show_help(self.__args_list):
            self.help(self.__args_list[0] if self.__args_list and self.__args_list[0] in self.option_dic else None)
            return
        if len(self.__args_list) < 1 or self.__args_list[0] not in self.option_dic:
            self.help()
            return
        self.option_dic[self.__args_list[0]](self.__args_list[1:])
