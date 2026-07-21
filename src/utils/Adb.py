import os
from command.Shell import Shell
from command.Base import Base, Opt
import Log

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
        self.pts = Shell.cmd('tty').stdout().replace('\n','')
        self.rootdir = self.tool_dir + '/data/adb/'
        self.sign = ['@','*']
        self.pst_root = self.rootdir + '.pst'
        if not os.path.exists(self.pst_root + self.pts[:self.pts.rfind('/')]):
            Shell.mkdir(self.pst_root + self.pts[:self.pts.rfind('/')]).status()
        if os.path.exists(self.pst_root + self.pts):
            with open(self.pst_root + self.pts, "r", encoding='UTF-8')as f:
                self.cur_dir = f.readline()
            f.close()
        else:
            with open(self.pst_root + self.pts, "w",encoding='UTF-8') as f:
                f.write('/')
                self.cur_dir = '/'
                self.__adb_root().status()
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
        Log.tips('\t'.join(out))

    def __adb_root(self):
        return Shell.chain().cmd('adb', 'root').cmd('adb', 'remount').cmd('adb', 'disable-verity')
    
    def __adb_cmd(self,cmd:str):
        status = Shell.cmd('adb', 'root').stderr()
        if status:
            Log.error(status.strip())
            return None
        return Shell.cmd('adb', 'shell', cmd)

    def __adb_stdout(self, cmd):
        adb = self.__adb_cmd(cmd)
        return adb.stdout() if adb else ''

    def __adb_status(self, cmd):
        adb = self.__adb_cmd(cmd)
        return adb.status() if adb else 1
    def __adb_dest_file(self, f):
        return f.replace('/', '#')

    def __adb_src_file(self,f):
        return f.replace('#', '/')
      
    def __pwd(self,arg:list):
        Log.tips(self.cur_dir)
    def __ls(self,arg:list):
        sub=''
        if not arg: 
            arg = ["/"]
        if arg[0][0] == '-':
            sub=arg[0]
        self.__pase_out(self.__adb_stdout('ls -F %s %s' %(sub,self.cur_dir + arg[-1])))
    def __cd(self,arg:list):
        self.cur_dir = self.__adb_stdout('cd %s && pwd' % Shell.format([arg[-1]])).replace('\n','')
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
        self.__adb_status('cp %s %s' %(src_prefix + arg[-2],dest_prefix + arg[-1]))

    def __mv(self,arg:list):
        if arg[-1][0] == '/':
            dest_prefix = ''
        elif arg[-1][0] != '/' :
              dest_prefix  = self.cur_dir + '/'
        if arg[-2][0] == '/':
            src_prefix = ''
        elif arg[-2][0] != '/' :
              src_prefix  = self.cur_dir + '/'
        self.__adb_status('mv %s %s' %(src_prefix + arg[-2],dest_prefix + arg[-1]))
        pass

    def __code(self, arg:list):
        if arg[-1][0] != '/':
            srcfile = self.cur_dir + '/' + ''.join(arg[-1])
        else:
            srcfile = arg[-1]
        dire = self.rootdir  + srcfile
        if not os.path.exists(dire[:dire.rfind('/')]):
            Shell.mkdir(dire[:dire.rfind('/')]).status()
        self.__adb_root() \
            .cmd('adb', 'pull', srcfile, dire) \
            .cmd('code', '-w', dire) \
            .cmd('adb', 'push', dire, srcfile) \
            .status()
    def __adb_shell(self, arg:list):
        self.__adb_root().cmd('adb', 'shell').status()
    def __push(self, arg:list):
        if arg[-1][0] == '/':
              cur_dir = arg[-1][0]
        else:
            cur_dir = os.path.realpath(arg[-1])
        for parent, dirnames, filenames in os.walk(cur_dir):
            for dirname in dirnames:
                dir_path = os.path.join(parent, dirname)
                Log.debug(dir_path)

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
        files = Shell.cmd('adb', 'shell', 'ls -F ' + arg[0:l]).stdout()
        return self.__pase_file(files)
    def __screen(self,arg:list):
        if not arg:
            self.help('screen')
            return
        choices = self.__screen_choices()
        if arg[0] == choices[0]:
            self.__adb_status("echo  '1 > /sys/class/backlight/panel0-backlight/bl_power'")
        elif  arg[0] == choices[1]:
            self.__adb_status("echo  '0 > /sys/class/backlight/panel0-backlight/bl_power'")
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

    def completion_spec(self):
        adb_files = self.__file
        return {
            'ls': {'_values': adb_files},
            'cd': {'_values': adb_files},
            'mv': {'_values': adb_files},
            'code': {'_values': adb_files},
            'screen': {'_values': self.__screen_choices},
            'cp': {'_values': adb_files},
            'pwd': {},
            'push': {},
        }
    
    def exec(self):
        # 空命令或未知命令默认进入 adb shell，保留原来的使用习惯。
        return self.dispatch(self.__args_list, default=self.__adb_shell)
