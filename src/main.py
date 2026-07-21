import os
import sys
import ast

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
    EXCLUDE_UTILS = {"__init__.py", "__pycache__/", "Completion.py"}

    def __init__(self, args=None):
        super().__init__(args)
        self.meta("hikrun 顶层入口：分发 Python 工具、shell 脚本和脚本目录。", args="<工具|脚本> [参数]")
        for name, desc in self._python_tools().items():
            self.command(name, desc)

    def _utils_dir(self):
        return self.tool_path('src', 'utils') + '/'

    def _tool_summary(self, path):
        try:
            with open(path, encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=path)
        except Exception as e:
            Log.debug("读取工具描述失败 %s: %s" % (path, e))
            return "Python 工具"

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (
                isinstance(func, ast.Attribute)
                and func.attr == "meta"
                and isinstance(func.value, ast.Name)
                and func.value.id == "self"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                continue
            return node.args[0].value
        return "Python 工具"

    def _python_tools(self):
        tools = {}
        for filename in self.files(self._utils_dir(), exclude=list(self.EXCLUDE_UTILS)):
            if not filename.endswith('.py'):
                continue
            name = filename[:-3].lower()
            tools[name] = self._tool_summary(os.path.join(self._utils_dir(), filename))
        return dict(sorted(tools.items()))

    def _get_app(self):
        return list(self._python_tools())

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
