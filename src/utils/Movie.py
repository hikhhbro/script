
from Base import Base
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
    def __init__(self, args=None):
        super().__init__(args)
        self.meta("影视搜索、同步和下载入口。")
        self.command("search", "搜索影视资源").run(self.search).args("<关键字>")
        self.command("sync", "同步影视数据").run(self.sync)
        self.command("download", "下载影视资源").run(self.download)
        self.command("show", "展示已记录资源").run(self.show)
        
        self.web_dic = self.config_read(web, merge=True)
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
