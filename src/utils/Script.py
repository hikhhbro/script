import os
from command.Shell import Shell
from command.CompTemp import CompTemp
from command.Listdirs import CurFile

class Script():
    def __init__(self, args_list=None):
        self.root_dir = os.getenv('SCRIPT_TOP_DIR')
        self.__args_list = args_list or []
        self.option_dic = {
            'readme' : self.__readme,
            'build' : self.__build,
            'rm' : self.__readme,
            'add' : self.__add,
        }
        self.shell_dir = self.root_dir + '/shell'
        self.company_shell_dir = self.root_dir + '/shell/company'
    def __readme(self,text = None):
        Shell('code /%s/README.md' % self.root_dir).exe()
        
    
    def __build(self,text = None):
        dir_opt = CurFile(self.shell_dir).get_file_opt(is_ = ["exe_file"])
        CompTemp().set(dir_opt)
            
        # print(dir_opt)
    def __rm(self,text = None):
        pass
    def __add(self,text = None):
        s = Shell()
        s.input('code %s/%s' % (self.shell_dir,text[-1]))
        s.input("chmod 777  %s/%s" % (self.shell_dir,text[-1]))
        s.exe()
        CompTemp().set([text[-1]])
        
        

    def _opt(self):
        return list(self.option_dic.keys())
    
    # def add_opt(self):
    #     return list(self.option_dic.keys())

    def exec(self):
        self.option_dic[self.__args_list[0]](self.__args_list[1:]) 

