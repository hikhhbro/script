import os
from shell import Shell
root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
class Adb():
    def __init__(self, args_list=None):
        super().__init__(opt=['/'])
        self.__args_list = args_list or ['/']
        self.todo_dic = { }
        self.pts = Shell('tty').exe().replace('\n','')
        self.rootdir = root_dir + '/adb_file/'
        self.sign = ['@','*']
        self.shell = 'adb shell '
        if os.path.exists(self.rootdir + self.pts):
            with open(self.rootdir + self.pts, "r", encoding='UTF-8')as f:
                self.cur_dir = f.readline()
            f.close()
        else:
            with open(self.rootdir + self.pts, "w",encoding='UTF-8') as f:
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
        }

    def get_default_opt(self):
        l = self.__args_list[-1].rfind('/')
        if l == -1 :
            self.__args_list[-1] = '/'
        self.files = Shell('adb shell ls -F ' + self.__args_list[-1][0:l]).exe()
        return self.pase()
        
    def pase(self):
        out = []
        file_list = self.files.split('\n')
        file_list = list(filter(None, file_list))
        for i in range(len(file_list)):
            if file_list[i][-1] in self.sign:
                out.append(file_list[i][:-1])
            else :
                out.append(file_list[i])
        return out

    
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
        return Shell(self.shell + cmd)
    def __pwd(self,arg:list):
        print(self.cur_dir)
    def __ls(self,arg:list):
        self.__pase_out(self.__adb_cmd('ls -F %s' %(self.cur_dir)).exe())
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
    def __adb_dest_file(self, f):
        return f.replace('/', '#')

    def __adb_src_file(self,f):
        return f.replace('#', '/')

    def __code(self, arg:list):
        srcfile = ''.join(arg[-1])
        dire = root_dir + '/adb_file/' + self.__adb_dest_file(srcfile)
        s = Shell()
        s.input('adb pull ' + srcfile + ' ' + dire)
        s.input('code ' + dire)
        s.exec_system()
        a = input("是否保存至手机: 回车")
        s.input('adb push ' + dire + ' ' + srcfile )
        s.exec_system()

    def exec(self):
        self.option_dic[self.__args_list[0]](self.__args_list[1:]) 