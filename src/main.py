import os
import sys
import time
import copy
import importlib
import subprocess
import logging
sys.path.append(os.getenv('SCRIPT_TOP_DIR')+"/src")
from command.Base import Base ,Myclass,Arg
from command.Json import Json
from command.CompTemp import CompTemp
from command.Log import Log
from command.Shell import Shell
from command.Listdirs import CurFile

if sys.argv[-1] == "-v":
    Log.config(Log.DEBUG)
    del sys.argv[-1]
elif sys.argv[-1] == "-vv":
    Log.config(Log.NOTSET)
    del sys.argv[-1]
else:
    Log.config(Log.INFO)
    
class Code():
    def __init__(self, args=None):
        self.__dic = {
            '-c': self.__company_file,
            '-adb': self.__adb_file,
            '-adb-sync': self.__adb_sync_file,
            None: self.__open_file
        }
        
        self.__args_list = args or []

    def __code_file(self, f):
        if os.path.isfile(f):
            Shell('code ' + f).exe()

        s = Shell()
        s.input('cp ' + root_dir + '/' + '.template ' + f)
        s.input("code " + f)
        s.exe()

    def __company_file(self, args_list):
        f = root_dir + '/' + 'company/' + ''.join(args_list[-1])
        self.__code_file(f)

    def __script_file(self, args_list):
        f = root_dir + '/' + 'script/' + ''.join(args_list[-1])
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
        s = Shell()
        s.input('adb root')
        s.input('adb remount')
        s.input('adb disable-verity')
        s.input('adb pull ' + srcfile + ' ' + dire)
        s.input('code -w ' + dire)
        s.exec_system()
        s.input('adb push ' + dire + ' ' + srcfile )
        s.exec_system()


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
            dir_tmp = 'script/'
        f = root_dir + '/' + dir_tmp + ''.join(self.__args_list[-1])
        resycle = root_dir + '/' + dir_tmp + \
            '.resycle/' + ''.join(self.__args_list[-1])
        Shell('mv ' + f + ' ' + resycle).exe()

class Git():
    def __init__(self, args_list=None):
        self.__args_list = args_list or []
        self.add_dic = { }
    def __find_git(self):
        return  True if Shell('git rev-parse --is-inside-work-tree').exe() == 'true\n' else False
    def __get_path(self):
        return Shell('pwd').exe()[:-1]

    def __get_remote(self):
        return Shell('git remote -v').exe().split('\n')[0]
    def __get_branch(self):
        return Shell("git branch | sed -n '/\* /s///p'").exe()[:-1]


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






# run = {
#     '--code': lambda args_list:  Code(args_list).run(),
#     '--rm': lambda args_list: Rm(args_list).run(),
#     '--git':lambda args_list: Git(args_list).run(),
#     'todo':lambda args_list: hikrun_todo(args_list).run(),
#     'adb':lambda args_list: hikrun_adb(args_list).exec(),
#     'cd':lambda args_list: hikrun_cd(args_list).exec(),
#     'script':lambda args_list: hikrun_script(args_list).run(),
# }


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
    def __init__(self, args_list=None):
        super().__init__()
        self.comp = Json('/data/.complete.json')
        self.shell_dir = self.tool_dir + '/shell'
    def _opt(self):
        if '/' in self.cur:
            return  CurFile(self.shell_dir).get_file_opt(self.cur,["exe_file","dir"],['data/'])
        else:
            return  CurFile(self.shell_dir).get_file_opt(self.cur,["exe_file","dir"],['data/']) +['todo','adb','cd','script','build','repo','readcode','flash']


def run():
    tmp_arg = Arg()
    if  CompTemp().get(tmp_arg.arg_list[0]):
        exr_file = os.getenv('SCRIPT_TOP_DIR') + "/shell/" + tmp_arg.arg_list[0]
        if os.path.exists(exr_file):
            Shell().exec_script(exr_file,tmp_arg.arg_list[1:])
    else:
        myclass = Myclass()
        module = myclass.get_sub_tool()
        module(tmp_arg.arg_list[1:]).exec()

if __name__ == '__main__':
    run()


