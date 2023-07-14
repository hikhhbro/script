from distutils.debug import DEBUG
import os
import sys
import copy
from command.Shell import Shell
from command.Listdirs import CurFile
import importlib
import logging
class Arg():
    def __init__(self):
        self.arg_list = copy.copy(sys.argv)
        if self.arg_list[-1] in  ['n','y']:
            self.isend  = True if self.arg_list[-1] == 'y' else False
            del  self.arg_list[-1]
        else :
            self.isend = None

        if self.arg_list[0][-3:] == '.py' or '/' + os.getenv('SCRIPT_TOOL_NAME') in self.arg_list[0]:
            del self.arg_list[0]
        if self.isend == False:
            self.cur =   self.arg_list[-1]
            del  self.arg_list[-1]
        else :
            self.cur = ''
            
    def last_cur(self,num):
        if len(self.arg_list) < 2:
            return self.cur
        if self.cur and num < len(self.arg_list):
            return self.arg_list[-(num+1)]
        return ''
          
        


class Base(Arg):
    def __init__(self,args_list:list = None):
        super().__init__()
        self.tool_dir = os.getenv('SCRIPT_TOP_DIR')
        self.tool_name = os.getenv("SCRIPT_TOOL_NAME")
        self.option_dic = {}
        self.data_dir = self.tool_dir + '/data/' 
    
    def _opt(self):
        return list(self.option_dic.keys())
    def exec(self):
        self.option_dic[self.arg_list[1]](self.arg_list[2:]) 
        


        



class Myclass():
    def __init__(self):
        sys.path.append(os.getenv('SCRIPT_TOP_DIR')+"/src/utils")
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

    def get_opname(self,last=1):
        if len(self.arg.arg_list) > 0 and last <= len(self.arg.arg_list):
            if self.arg.arg_list[-last][0] != '-':
                return  self.arg.arg_list[-last]
            return ""
        else :
            return ''    


class Opt():
    def __init__(self,opt=None,file_opt = False):
        self.opt = {
          "long":["--help"],
          "short":[],
          "sub":[]
        }
        self.file_opt = file_opt
        if opt:
          if isinstance(opt,list):
            for item in opt:
              self.opt_type(item).append(item)
          else :
              self.opt_type(opt).append(item)

    def get_long_opt(self):
      return self.opt["long"]

    def get_short_opt(self):
      return self.opt["short"]

    def get_sub_opt(self):
      return self.opt["sub"]

    def set_long_opt(self,opt):
      if isinstance(opt,list):
        self.opt["long"] = self.opt["long"] + opt
      else :
        self.opt["long"].append(opt)

    def set_short_opt(self,opt):
      if isinstance(opt,list):
        self.opt["short"] = self.opt["short"] + opt
      else :
        self.opt["short"].append(opt)

    def set_sub_opt(self,opt):
      if isinstance(opt,list):
        self.opt["sub"] = self.opt["sub"] + opt
      else :
        self.opt["sub"].append(opt)
        


    def opt_type(self,arg):
      if '--' == arg[0:2] :
          opt = self.get_long_opt()
      elif '-' in arg[0] :
          opt = self.get_short_opt()
      else :
          opt = self.get_sub_opt()
      return opt
  