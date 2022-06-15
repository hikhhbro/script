import os
import sys
from command.Shell import Shell
from command.Listdirs import CurFile
import importlib
class Base():
    def __init__(self,args_list:list):
        self.tool_dir = os.getenv('SCRIPT_TOP_DIR')
        self.__args_list = args_list or []
        self.option_dic = {}
    
    def _opt(self):
        return list(self.option_dic.keys())
    def run(self):
        self.option_dic[self.__args_list[0]](self.__args_list[1:]) 
        

class Myclass():
    def __init__(self):
        sys.path.append(os.getenv('SCRIPT_TOP_DIR')+"/src/utils")
        tmp = sys.argv
        self.isend = True if tmp[-1] == 'y' else False
        self.asgs_list = tmp[1:-1] if "complete.py" in tmp[0] else tmp[:-1]    
        if self.isend :
            self.cur = [''] 
        else :
            self.cur = [self.asgs_list[-1]] 
            del self.asgs_list[-1]  
    def get_sub_tool(self):
        if len(self.asgs_list) == 1:
            out  = self.asgs_list[0]
        else :
            out  = self.asgs_list[1]
        model = importlib.import_module(out)
        return getattr(model,out)
    
    def get_class(self):
        if len(self.asgs_list) == 1 and self.asgs_list[0] == os.getenv('SCRIPT_TOOL_NAME') :
            out = "main"
            package='main'
        else:
            out=""
        del self.asgs_list[0]
        if self.isend :
            if len(self.asgs_list) > 0:
                out = self.asgs_list[0].capitalize()
                del self.asgs_list[0]
        else :
            if len(self.asgs_list) > 0:
                out =  self.asgs_list[0].capitalize()
                del self.asgs_list[0]
        model = importlib.import_module(out)
        return getattr(model,out)

    def get_opname(self):
        if self.isend :
            if len(self.asgs_list) > 0:
                if self.asgs_list[0][0] != '-':
                    return  self.asgs_list[0]
            else :
                return ''    
        else :
            if len(self.asgs_list) > 0:
                if self.asgs_list[0][0] != '-':
                    return  self.asgs_list[0]
            else :
                return ''    
