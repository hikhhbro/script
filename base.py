import os
import sys
import compile
from shell import Shell

class Base():
    def __init__(self, opt=None):
        self.opt = opt or []
        self.opt.append('--help')
        self.setspace = {True: 'compopt +o nospace',
                         False: 'compopt -o nospace'}
        self.out_list = []
        self.default_opt = True
        self.isend = True if sys.argv[-1] == 'y' else False
        self.asgs_list = sys.argv[1:-1] if "complete.py" in sys.argv[0] else sys.argv[:-1]
        self.get_arg_prefix = ''
    def get_last_input(self,arg_full=False):
        if arg_full :
            if self.isend :
                return None
            return self.asgs_list[-1]
        else :
            if self.isend or self.asgs_list[-1] == '/':
                return None
            l = self.asgs_list[-1].rfind('/')
            if l < 0:
                return self.asgs_list[-1]
            else:
                self.get_arg_prefix = self.asgs_list[-1][0:l+1]
                return self.asgs_list[-1][l+1:]

    def get_default_opt(self):
        return CurFile().get_file_opt(self.get_last_input(True))
    def get_opt(self, arg):
        if not arg or arg[-1] =='/':
            r = self.get_default_opt()
            if len(r) ==1 :
                r[0] = self.get_arg_prefix + r[0] 
            return r
        else :
            for item in self.opt:
                if len(arg) <= len(item) and arg == item[0:len(arg)]:
                    self.default_opt = False
                    self.out_list.append(item)
            if self.default_opt :
                for item in self.get_default_opt():
                    if len(arg) <= len(item) and arg == item[0:len(arg)]:
                        self.out_list.append(self.get_arg_prefix + item)
            return self.out_list


    def set_out(self, out_list):
        print(self.setspace[self.getlsspace()])
        print(' '.join(out_list))
    def getlsspace(self):
        if len(self.out_list) == 0 or (len(self.out_list) == 1 and self.out_list[-1][-1] == '/' or self.out_list[-1][-1] == '='):
            return False
        else:
            return True
    def get_cur_arg(self):
        if self.isend :
            return asgs_list[-1]
        else :
            if len(asgs_list) > 1:
                return asgs_list[-2]
            else:
                return None
        
    def get_cur(self):
        if  len(sys.argv) == 3 or (len(sys.argv) == 4 and sys.argv[-1] == 'n') :
            return  sys.argv[1]
        elif  len(sys.argv) > 4 :
            return sys.argv[2]
    #     if isend == True :
    #         self.__run_opt = None
    #         self.__arg_list  = arg or []
    #     else :
    #         self.__run_opt = arg[0]
    #         if arg == None  or len(arg) < 2:
    #             self.__arg_list = []
    #         else :
    #             self.__arg_list = arg[1:]

    # def in_opt(self,opt):
    #     return opt if opt in self.__opt else None

    def run(self):
        self.set_out( self.get_opt(self.get_last_input()))