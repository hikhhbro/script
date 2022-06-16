import os
from command.Shell import Shell
from command.Base import Base

class Adb(Base):
    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.__args_list = args_list or ['']
        self.todo_dic = { }
        self.pts = Shell('tty').exe().replace('\n','')
        self.rootdir = self.tool_dir + '/data/adb/'
        self.sign = ['@','*']
        self.shell = 'adb shell '
        self.pst_root = self.rootdir + '.pst'
        if not os.path.exists(self.pst_root + self.pts[:self.pts.rfind('/')]):
            Shell('mkdir -p '+ self.pst_root + self.pts[:self.pts.rfind('/')]).exec_system()
        if os.path.exists(self.pst_root + self.pts):
            with open(self.pst_root + self.pts, "r", encoding='UTF-8')as f:
                self.cur_dir = f.readline()
            f.close()
        else:
            with open(self.pst_root + self.pts, "w",encoding='UTF-8') as f:
                f.write('/')
                self.cur_dir = '/'
                Shell('adb root && adb remount && adb disable-verity').exe()
            f.close()
        self.option_dic = {
            'ls' : self.__ls,
            'cd' : self.__cd,
            'cp' : self.__cp,
            'mv' : self.__mv,
            'code' : self.__code,
            'pwd' : self.__pwd,
            'screen' : self.__screen,
            '' : self.__adb_shell
        }


    
    def __pase_out(self,out_file:str):
        out = []
        file_list = out_file.split('\n')
        file_list = list(filter(None, file_list))
        for i in range(len(file_list)):
            if file_list[i][-1] in self.sign:
                out.append(file_list[i][:-1])
            else :
                out.append(file_list[i])
        print('\t'.join(out))
    
    def __adb_cmd(self,cmd:str):
        status = Shell("adb root").exe("err")
        if not status :
            return Shell(self.shell + cmd)
        else :
            print(status)
            return Shell()
    def __adb_dest_file(self, f):
        return f.replace('/', '#')

    def __adb_src_file(self,f):
        return f.replace('#', '/')
      
    def __pwd(self,arg:list):
        print(self.cur_dir)
    def __ls(self,arg:list):
        sub=''
        if not arg: 
            arg = ["/"]
        if arg[0][0] == '-':
            sub=arg[0]
        self.__pase_out(self.__adb_cmd('ls -F %s %s' %(sub,self.cur_dir + arg[-1])).exe())
    def __cd(self,arg:list):
        self.cur_dir = self.__adb_cmd('cd "%s && pwd"' %arg[-1]).exe().replace('\n','')
        with open(self.rootdir + self.pts, "w",encoding='UTF-8') as f:
            f.write(self.cur_dir)
        f.close()
    def __cp(self,arg:list):
        if arg[-1][0] == '/':
            dest_prefix = ''
        elif arg[-1][0] != '/' :
              dest_prefix  = self.cur_dir + '/'
        if arg[-2][0] == '/':
            src_prefix = ''
        elif arg[-2][0] != '/' :
              src_prefix  = self.cur_dir + '/'
        self.__adb_cmd('cp %s %s' %(src_prefix + arg[-2],dest_prefix + arg[-1])).exe()

    def __mv(self,arg:list):
        if arg[-1][0] == '/':
            dest_prefix = ''
        elif arg[-1][0] != '/' :
              dest_prefix  = self.cur_dir + '/'
        if arg[-2][0] == '/':
            src_prefix = ''
        elif arg[-2][0] != '/' :
              src_prefix  = self.cur_dir + '/'
        self.__adb_cmd('mv %s %s' %(src_prefix + arg[-2],dest_prefix + arg[-1])).exe()
        pass

    def __code(self, arg:list):
        if arg[-1][0] != '/':
            srcfile = self.cur_dir + '/' + ''.join(arg[-1])
        else:
            srcfile = arg[-1]
        dire = self.rootdir  + srcfile
        if not os.path.exists(dire[:dire.rfind('/')]):
            Shell('mkdir -p '+ dire[:dire.rfind('/')] ).exec_system()
        s = Shell()
        s.input('adb root')
        s.input('adb remount')
        s.input('adb disable-verity')
        s.input('adb pull ' + srcfile + ' ' + dire)
        s.input('code -w ' + dire)
        s.exec_system()
        s.input('adb push ' + dire + ' ' + srcfile )
        s.exec_system()
    def __adb_shell(self, arg:list):
        s = Shell()
        s.input('adb root')
        s.input('adb remount')
        s.input('adb disable-verity')
        s.input('adb shell')
        s.exec_system()
#补全
#adb 文件补全
    def __pase_file(self,out_file:str):
        out = []
        file_list = out_file.split('\n')
        file_list = list(filter(None, file_list))
        for i in range(len(file_list)):
            if file_list[i][-1] in self.sign:
                out.append(file_list[i][:-1])
            else :
                out.append(file_list[i])
        return out
    def __file(self):
        arg = ''
        if  self.__args_list : 
            arg = ''.join(self.__args_list)
        if not arg or arg[0] != '/':
            arg = self.cur_dir + '/' + arg
        l = arg.rfind('/')
        if l == -1 :
            arg = '/'
        files = Shell('adb shell ls -F ' + arg[0:l]).exe()
        return self.__pase_file(files)
    def __screen(self,arg:list):
        if arg[0] == self.screen_opt()[0]:
            self.__adb_cmd('echo  \'1 > /sys/class/backlight/panel0-backlight/bl_power\'').exe()
        elif  arg[0] == self.screen_opt()[1]:
            self.__adb_cmd('echo  \'0 > /sys/class/backlight/panel0-backlight/bl_power\'').exe()
#adb 子命令补全选项
    def _opt(self):
        return list(self.option_dic.keys())
#adb ls 补全选项
    def ls_opt(self):
        return self.__file()
#adb cd 补全选项
    def cd_opt(self):
        return self.__file()
#adb mv 补全选项
    def mv_opt(self):
        return self.__file()
#adb code 补全选项
    def code_opt(self):
        return self.__file()
#adb screen 补全选项
    def screen_opt(self):
        return ['close','open']
    
    def exec(self):
        self.option_dic[self.__args_list[0]](self.__args_list[1:]) 