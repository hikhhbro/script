import os
from command.Shell import Shell
from command.CompTemp import CompTemp
from command.Listdirs import CurFile
from command.Base import Base
from command.Base import Opt

class Script(Base):
    def __init__(self, args_list=None):
        super().__init__()
        self.option_dic = {
            'readme' : self.__readme,
            'build' : self.__build,
            'rm' : self.__rm,
            'add' : self.__add,
        }
        self.shell_dir = self.tool_dir + '/shell'
        self.company_shell_dir = self.tool_dir + '/shell/company'
    def __readme(self,text = None):
        Shell('code -w /%s/README.md' % self.tool_dir).exe()
        Shell('cd %s && git add README.md && git commit -m 更新READEME' % self.tool_dir).exe()
    
    def __build(self,text = None):
        dir_opt = CurFile(self.shell_dir).get_file_opt(is_ = ["exe_file"])
        CompTemp().set(dir_opt)
            
        # print(dir_opt)
    def __rm(self,text = None):
        try:
            Shell('mv  %s/%s %s/.resycle/%s' %(self.shell_dir,text[-1],self.shell_dir,text[-1])).exe()
            CompTemp().delete([text[-1]])
        except:
            print("文件不存在")
    def __add(self,text = None):
        s = Shell()
        s.input('code %s/%s' % (self.shell_dir,text[-1]))
        s.input("chmod 777  %s/%s" % (self.shell_dir,text[-1]))
        s.exe()
        CompTemp().set([text[-1]])
        
    def add_opt(self):
        return Opt(CurFile(self.shell_dir).get_file_opt(self.cur))

    def rm_opt(self):
        return self.add_opt()

