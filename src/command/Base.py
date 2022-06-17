import os
import sys
import copy
from command.Shell import Shell
from command.Listdirs import CurFile
import importlib
class Arg():
    def __init__(self):
        self.arg_list = copy.copy(sys.argv)
        if self.arg_list[-1] in  ['n','y']:
            self.isend  = True if self.arg_list[-1] == 'y' else False
            del  self.arg_list[-1]
        else :
            self.isend = None

        if self.arg_list[0][-3:] == '.py':
            del self.arg_list[0]
        if self.isend == False:
            self.cur =   self.arg_list[-1]
            del  self.arg_list[-1]
        else :
            self.cur = ''
        


class Base(Arg):
    def __init__(self,args_list:list = None):
        super().__init__()
        self.tool_dir = os.getenv('SCRIPT_TOP_DIR')
        self.option_dic = {}
    
    def _opt(self):
        return list(self.option_dic.keys())
    def exec(self):
        self.option_dic[self.arg_list[1]](self.arg_list[2:]) 
        


        



class Myclass():
    def __init__(self):
        sys.path.append(os.getenv('SCRIPT_TOP_DIR')+"/src/utils")
        # tmp = copy.copy(sys.argv)
        # self.isend = True if tmp[-1] == 'y' else False
        # if tmp[-1]  in ['n','y']:
        #     self.asgs_list = tmp[1:-1] if "complete.py" in tmp[0] or "main.py" in tmp[0] else tmp[:-1]   
        # else:
        #     self.asgs_list = tmp
        # if self.isend :
        #     self.cur = [''] 
        # else :
        #     self.cur = [self.asgs_list[-1]] 
        #     del self.asgs_list[-1]  
        self.arg = Arg()
    def get_sub_tool(self):
        out  = self.arg.arg_list[0]
        model = importlib.import_module(out.capitalize())
        return getattr(model,out.capitalize())
    
    def get_class(self):
        if len(self.arg.arg_list) == 1 and self.arg.arg_list[0] == os.getenv('SCRIPT_TOOL_NAME') :
            out = "main"
            package='main'
        else :
            out=""
        del self.arg.arg_list[0]
        if self.arg.isend :
            if len(self.arg.arg_list) > 0:
                out = self.arg.arg_list[0].capitalize()
                del self.arg.arg_list[0]
        else :
            if len(self.arg.arg_list) > 0:
                out =  self.arg.arg_list[0].capitalize()
                del self.arg.arg_list[0]
        model = importlib.import_module(out)
        return getattr(model,out)

    def get_opname(self):
        if self.arg.isend :
            if len(self.arg.arg_list) > 0:
                if self.arg.arg_list[0][0] != '-':
                    return  self.arg.arg_list[0]
            else :
                return ''    
        else :
            if len(self.arg.arg_list) > 0:
                if self.arg.arg_list[0][0] != '-':
                    return  self.arg.arg_list[0]
            else :
                return ''    
