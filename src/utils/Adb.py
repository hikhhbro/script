import os
from command.Shell import Shell
from command.Base import Base, Opt

class Adb(Base):
    help_summary = "在 adb shell 上执行常用文件、目录和屏幕操作。"
    help_usage = "{tool_name} adb <子命令> [参数]"
    help_options = {
        "ls": "列出设备当前目录文件",
        "cd": "切换记录的设备当前目录",
        "cp": "在设备内复制文件",
        "mv": "在设备内移动文件",
        "code": "拉取设备文件到本地编辑后推回",
        "pwd": "显示记录的设备当前目录",
        "screen": "打开或关闭屏幕背光",
        "push": "推送本地文件到设备",
        "--help": "显示当前帮助",
    }
    help_examples = [
        "hikrun adb ls",
        "hikrun adb cd /system",
        "hikrun adb code /system/build.prop",
    ]

    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.__args_list = self.args
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
        self.set_commands({
            'ls' : self.__ls,
            'cd' : self.__cd,
            'cp' : self.__cp,
            'mv' : self.__mv,
            'code' : self.__code,
            'pwd' : self.__pwd,
            'screen' : self.__screen,
            'push':self.__push,
            '' : self.__adb_shell
        })


    
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
        with open(self.pst_root + self.pts, "w",encoding='UTF-8') as f:
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
    def __push(self, arg:list):
        if arg[-1][0] == '/':
              cur_dir = arg[-1][0]
        else:
            cur_dir = os.path.realpath(arg[-1])
        for parent, dirnames, filenames in os.walk(cur_dir):
            for dirname in dirnames:
                dir_path = os.path.join(parent, dirname)
                Shell()

# 补全：adb 文件补全
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
        if not arg:
            self.help('screen')
            return
        choices = self.__screen_choices()
        if arg[0] == choices[0]:
            self.__adb_cmd("echo  '1 > /sys/class/backlight/panel0-backlight/bl_power'").exe()
        elif  arg[0] == choices[1]:
            self.__adb_cmd("echo  '0 > /sys/class/backlight/panel0-backlight/bl_power'").exe()
# adb 子命令补全选项
    def _opt(self):
        return super()._opt()
# adb ls 补全选项
    def ls_opt(self):
        return Opt(self.__file())
# adb cd 补全选项
    def cd_opt(self):
        return Opt(self.__file())
# adb mv 补全选项
    def mv_opt(self):
        return Opt(self.__file())
# adb code 补全选项
    def code_opt(self):
        return Opt(self.__file())
# adb screen 补全选项
    def __screen_choices(self):
        return ['close', 'open']

    def screen_opt(self):
        return Opt(self.__screen_choices())
    
    def exec(self):
        # 空命令或未知命令默认进入 adb shell，保留原来的使用习惯。
        return self.dispatch(self.__args_list, default=self.__adb_shell)
