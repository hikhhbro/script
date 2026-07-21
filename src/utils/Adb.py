import os
from command.Shell import Shell
from command.Base import Base
import Log

class Adb(Base):
    def __init__(self, args=None):
        super().__init__(args)
        self.meta("在 adb shell 上执行常用文件、目录和屏幕操作。")
        self.pts = Shell.cmd('tty').stdout().replace('\n','')
        self.sign = ['@','*']
        self.ensure_dir(os.path.dirname(self.__state_path()))
        if os.path.exists(self.__state_path()):
            with open(self.__state_path(), "r", encoding='UTF-8')as f:
                self.cur_dir = f.readline()
            f.close()
        else:
            with open(self.__state_path(), "w",encoding='UTF-8') as f:
                f.write('/')
                self.cur_dir = '/'
                self.__adb_root().status()
            f.close()
        self.command('ls', '列出设备当前目录文件').run(self.__ls).value(self.__file).args("[路径]")
        self.command('cd', '切换记录的设备当前目录').run(self.__cd).value(self.__file).args("<路径>")
        self.command('cp', '在设备内复制文件').run(self.__cp).value(self.__file).args("<源> <目标>")
        self.command('mv', '在设备内移动文件').run(self.__mv).value(self.__file).args("<源> <目标>")
        self.command('code', '拉取设备文件到本地编辑后推回').run(self.__code).value(self.__file).args("<设备文件>")
        self.command('pwd', '显示记录的设备当前目录').run(self.__pwd)
        self.command('screen', '打开或关闭屏幕背光').run(self.__screen).value(self.__screen_choices).args("<open|close>")
        self.command('push', '推送本地文件到设备').run(self.__push).args("<本地路径>")
        self.default(self.__adb_shell)


    
    def __parse_file_list(self,out_file:str):
        return [
            item[:-1] if item[-1] in self.sign else item
            for item in out_file.splitlines()
            if item
        ]

    def __print_file_list(self,out_file:str):
        Log.tips('\t'.join(self.__parse_file_list(out_file)))

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
    def __state_path(self):
        return self.data_path('.pst', self.pts.lstrip('/'))

    def __device_path(self, path):
        return path if path.startswith('/') else self.cur_dir + '/' + path
      
    def __pwd(self,arg:list):
        Log.tips(self.cur_dir)

    def __ls(self,arg:list):
        sub=''
        if not arg: 
            arg = ["/"]
        if arg[0][0] == '-':
            sub=arg[0]
        self.__print_file_list(self.__adb_stdout('ls -F %s %s' %(sub, self.__device_path(arg[-1]))))

    def __cd(self,arg:list):
        self.cur_dir = self.__adb_stdout('cd %s && pwd' % Shell.format([arg[-1]])).strip()
        with open(self.__state_path(), "w",encoding='UTF-8') as f:
            f.write(self.cur_dir)
        f.close()

    def __cp(self,arg:list):
        src, dest = arg[-2:]
        self.__adb_status('cp %s %s' % (self.__device_path(src), self.__device_path(dest)))

    def __mv(self,arg:list):
        src, dest = arg[-2:]
        self.__adb_status('mv %s %s' % (self.__device_path(src), self.__device_path(dest)))

    def __code(self, arg:list):
        srcfile = self.__device_path(arg[-1])
        dire = self.data_path(srcfile.lstrip('/'))
        self.ensure_dir(os.path.dirname(dire))
        self.__adb_root() \
            .cmd('adb', 'pull', srcfile, dire) \
            .cmd('code', '-w', dire) \
            .cmd('adb', 'push', dire, srcfile) \
            .status()
    def __adb_shell(self, arg:list):
        self.__adb_root().cmd('adb', 'shell').status()
    def __push(self, arg:list):
        cur_dir = arg[-1] if arg[-1].startswith('/') else os.path.realpath(arg[-1])
        for parent, dirnames, filenames in os.walk(cur_dir):
            for dirname in dirnames:
                dir_path = os.path.join(parent, dirname)
                Log.debug(dir_path)

    def __file(self):
        arg = ''
        if self.args:
            arg = ''.join(self.args)
        arg = self.__device_path(arg) if arg else self.cur_dir + '/'
        parent = os.path.dirname(arg) or '/'
        files = Shell.cmd('adb', 'shell', 'ls -F ' + parent).stdout()
        return self.__parse_file_list(files)
    def __screen(self,arg:list):
        if not arg:
            self.help('screen')
            return
        choices = self.__screen_choices()
        if arg[0] == choices[0]:
            self.__adb_status("echo  '1 > /sys/class/backlight/panel0-backlight/bl_power'")
        elif  arg[0] == choices[1]:
            self.__adb_status("echo  '0 > /sys/class/backlight/panel0-backlight/bl_power'")
    def __screen_choices(self):
        return ['close', 'open']
    
    def exec(self):
        # 空命令或未知命令默认进入 adb shell，保留原来的使用习惯。
        return self.dispatch(default=self.__adb_shell)
