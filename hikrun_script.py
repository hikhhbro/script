import os
from shell import Shell
class hikrun_script():
    def __init__(self, args_list=None):
        self.root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
        self.__args_list = args_list or []
        self.option_dic = {
            'readme' : self.__readme,
            'build' : self.__build,
            'rm' : self.__readme,
            'add' : self.__add,
        }
    def __readme(self,text = None):
        Shell('code /%s/README.md' % self.root_dir).exe()
    def __build(self,text = None):
        pass
    def __rm(self,text = None):
        pass
    def __add(self,text = None):
        pass

    def _opt(self):
        return list(self.option_dic.keys())

    def run(self):
        self.option_dic[self.__args_list[0]](self.__args_list[1:]) 

