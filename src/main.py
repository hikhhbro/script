import os
import sys

sys.path.append(os.getenv('SCRIPT_TOP_DIR')+"/src")
sys.path.append(os.getenv('SCRIPT_TOP_DIR')+"/src/command")
from Base import Base,Myclass,Arg
from CompTemp import CompTemp
from Shell import Shell

import Log


fmt = '%(asctime)s - %(levelname)-7s %(filename)s:%(lineno)-10d %(message)s'
datefmt ='%Y/%m/%d %H:%M:%S'

if sys.argv[-1] == "-v":
    Log.basicConfig(level=Log.DEBUG, format=fmt,datefmt=datefmt)
    del sys.argv[-1]
elif sys.argv[-1] == "-vv":
    Log.basicConfig(level=Log.NOTSET, format=fmt,datefmt=datefmt)
    del sys.argv[-1]
else:
    Log.basicConfig(level=Log.INFO, format=fmt,datefmt=datefmt)


class main(Base):
    def __init__(self, args=None):
        super().__init__(args)
        self.meta("hikrun 顶层入口：分发 Python 工具、shell 脚本和脚本目录。", args="<工具|脚本> [参数]")
        self.command("build", "构建工程")
        self.command("repo", "比较 repo manifest")
        self.command("adb", "adb 常用操作")
        self.command("movie", "影视资源工具")
        self.command("flash", "工程烧录工具")
        self.command("cd", "终端目录跳转")
        self.command("script", "管理 shell 脚本")
        self.command("todo", "待办事项")
        self.command("readcode", "代码阅读辅助")
        self.command("note", "笔记管理")
        self.command("winsh", "Windows 命令桥接")

    def _get_app(self):
      apps_list = self.files(self.tool_path('src', 'utils') + '/', exclude=["__init__.py","__pycache__/","Completion.py"])
      for i in range(len(apps_list)):
        apps_list[i] = apps_list[i].split('.')[0].lower()
      return apps_list


    def complete(self, ctx):
        cur = ctx.current
        if '/' in cur:
            return self.file_opt(self.shell_path(), cur, ["exe_file","dir"], [])
        return self.completion(self.files(self.shell_path(), cur, ["exe_file","dir"], ['data/']) + self._get_app())


def run():
    tmp_arg = Arg()
    if not tmp_arg.arg_list:
        main([]).help()
        return
    if tmp_arg.arg_list[0] in {"--help", "-h", "help"}:
        # 顶层帮助只处理第一个参数，模块级 --help 交给对应模块。
        main(tmp_arg.arg_list[1:]).help()
        return
    if CompTemp().get(tmp_arg.arg_list[0]) is not False:
        exr_file = os.getenv('SCRIPT_TOP_DIR') + "/shell/" + tmp_arg.arg_list[0]
        if os.path.exists(exr_file):
            Shell.cmd(exr_file, *tmp_arg.arg_list[1:]).status()
    else:
        myclass = Myclass()
        module = myclass.get_sub_tool()
        module(tmp_arg.arg_list[1:]).exec()

if __name__ == '__main__':
    run()
    # ds =  main()
    # ds.get_app()
