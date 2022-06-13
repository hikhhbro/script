import os
import sys
import compile
from shell import Shell
from hik_file import CurFile

class Base():
    def __init__(self,args_list:list):
        self.root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
        self.__args_list = args_list or []
        self.option_dic = {}
    
    def _opt(self):
        return list(self.option_dic.keys())
    def run(self):
        self.option_dic[self.__args_list[0]](self.__args_list[1:]) 