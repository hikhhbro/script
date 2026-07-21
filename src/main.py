import os
import sys
import time
import copy
import importlib
import subprocess

sys.path.append(os.getenv('SCRIPT_TOP_DIR')+"/src")
sys.path.append(os.getenv('SCRIPT_TOP_DIR')+"/src/command")
from Base import Base,Myclass,Arg,Opt
from Json import Json
from CompTemp import CompTemp
from Shell import Shell
from Listdirs import CurFile

import Log


root_dir = os.getenv('SCRIPT_TOP_DIR') or os.getcwd()
dir_list = ['shell']


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
    
class Code():
    def __init__(self, args=None):
        self.__dic = {
            '-c': self.__company_file,
            '-adb': self.__adb_file,
            '-adb-sync': self.__adb_file,
            None: self.__open_file
        }
        
        self.__args_list = args or []

    def __code_file(self, f):
        if os.path.isfile(f):
            Shell.code(f).status()
            return

        Shell.chain().cmd('cp', os.path.join(root_dir, '.template'), f).cmd('code', f).status()

    def __company_file(self, args_list):
        f = root_dir + '/' + 'company/' + ''.join(args_list[-1])
        self.__code_file(f)

    def __script_file(self, args_list):
        f = root_dir + '/' + 'shell/' + ''.join(args_list[-1])
        self.__code_file(f)

    def __find_file(self, args_list):
        for item in dir_list:
            f = root_dir + '/' + item + '/' + args_list[-1]
            if os.path.isfile(f):
                return f

    def __open_file(self, args_list):
        f = self.__find_file(args_list)
        if f:
            self.__code_file(f)
        else:
            self.__script_file(args_list)

    def __adb_dest_file(self, f):
        return f.replace('/', '#')

    def __adb_src_file(self,f):
        return f.replace('#', '/')

    def __adb_file(self, args_list):
        srcfile = ''.join(args_list[-1])
        dire = root_dir + '/adb_file/' + self.__adb_dest_file(srcfile)
        Shell.chain() \
            .cmd('adb', 'root') \
            .cmd('adb', 'remount') \
            .cmd('adb', 'disable-verity') \
            .cmd('adb', 'pull', srcfile, dire) \
            .cmd('code', '-w', dire) \
            .cmd('adb', 'push', dire, srcfile) \
            .status()


    def run(self):
        if self.__args_list[0] in self.__dic:
            self.__dic[self.__args_list[0]](self.__args_list[1:])
        else:
            self.__dic[None](self.__args_list)


class Rm():
    def __init__(self, args_list=None):
        self.__args_list = args_list or []

    def run(self):
        if self.__args_list[0] == '-c':
            self.__args_list.pop(0)
            dir_tmp = 'company/'
        else:
            dir_tmp = 'shell/'
        f = root_dir + '/' + dir_tmp + ''.join(self.__args_list[-1])
        resycle = root_dir + '/' + dir_tmp + \
            '.resycle/' + ''.join(self.__args_list[-1])
        Shell.cmd('mv', f, resycle).status()

class Git():
    def __init__(self, args_list=None):
        self.__args_list = args_list or []
        self.add_dic = { }
    def __find_git(self):
        return Shell.cmd('git', 'rev-parse', '--is-inside-work-tree').stdout() == 'true\n'
    def __get_path(self):
        return os.getcwd()

    def __get_remote(self):
        return Shell.cmd('git', 'remote', '-v').stdout().split('\n')[0]
    def __get_branch(self):
        return Shell.bash(r"git branch | sed -n '/\* /s///p'").stdout()[:-1]


    def add(self):
        if self.__find_git():
            self.add_dic =  {self.__get_path():[self.__get_remote(),self.__get_branch()]}
    def print_add(self):
        for key, value in self.add_dic.items():
            # print(key,value[0],value[1])
            print("本地: %s |远程:%s | 分支: %s" % (key,value[0],value[1]))
    
    def run(self):
        if self.__args_list[-1] == 'add' :
            self.add()
            self.print_add()


def get_probe(f):
    index = f.rfind('/')
    if index != -1:
        return f[index+1:] + '_probe'
    return f + '_probe'


def get_file_path(f):
    for item in dir_list:
        if os.path.isfile(root_dir + '/' + item + '/' + f):
            return root_dir + '/' + item + '/' + f
    return None


def get_compile_path(f):
    for item in dir_list:
        if os.path.isfile(root_dir + '/' + '.compile/' + item  + '/' + f):
            return root_dir + '/' + '.compile/' + \
                item  + '/' + f


class main(Base):
    help_summary = "hikrun 顶层入口：分发 Python 工具、shell 脚本和脚本目录。"
    help_usage = "{tool_name} <工具|脚本> [参数]"
    help_options = {
        "build": "构建工程",
        "repo": "比较 repo manifest",
        "adb": "adb 常用操作",
        "movie": "影视资源工具",
        "flash": "工程烧录工具",
        "cd": "终端目录跳转",
        "script": "管理 shell 脚本",
        "todo": "待办事项",
        "readcode": "代码阅读辅助",
        "note": "笔记管理",
        "--help": "显示当前帮助",
    }
    help_examples = [
        "hikrun --help",
        "hikrun adb --help",
        "hikrun note code 工作/记录",
    ]

    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.comp = Json('/data/.complete.json')
        self.shell_dir = self.tool_dir + '/shell'
        self.app_dir = self.tool_dir + '/src/utils/'

    def _get_app(self):
      apps_list = CurFile(self.app_dir).get_file_opt(exclude=["__init__.py","__pycache__/","Completion.py"])
      for i in range(len(apps_list)):
        apps_list[i] = apps_list[i].split('.')[0].lower()
      return apps_list


    def _opt(self):
        if '/' in self.cur:
            return  Opt(CurFile(self.shell_dir).get_file_opt(self.cur,["exe_file","dir"],[]))
        else:
            return  Opt(CurFile(self.shell_dir).get_file_opt(self.cur,["exe_file","dir"],['data/']) + self._get_app())


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
