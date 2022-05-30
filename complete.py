import os
import sys
import compile
from shell import Shell


class Complete:
    def __init__(self, asgs=[]):
        self.end = asgs[-1]
        self.asgs = asgs
        self.asgs.pop()
        self.out = {}
        # self.hikrun = ['--rm', '--code']
        # self.setspace = {True: 'compopt +o nospace',
        #                  False: 'compopt -o nospace'}
        self.end_dic = {'n': False, 'y': True}

        # self.dir_list = ["script", 'company']

    def last_input(self):  # hikrun  wiz/w  -> wiz/w
        return self.asgs[-1]

    def last_2_input(self):
        if len(self.asgs) > 1:
            return self.asgs[-2]
        else:
            return None

    # def set_out(self, sw: bool):
    #     print(self.setspace[sw])
    #     print(' '.join(list(self.out.keys())))



    # def to_compile_path(path):
    #     return self.root_dir + '.compile/' + path[self.root_dir_len:]

    # def find_files(self, name=''):
    #     file_dir = {}
    #     for root, dirs, files in os.walk(self.root_dir+'/'+name):
    #         for d in dirs:
    #             if d[0] != '.':
    #                 file_dir['{}/'.format(d)] = root + '/' + d
    #         for file in files:
    #             if self.isexecutable(file):
    #                 file_dir[file] = root + '/' + file
    #         break
    #     return file_dir

#     def get_file_name(self, file):
#         if self.last_input().rfind('/') != -1:
#             return file[self.last_input().rfind('/'):]
#         return file

#     def matching_file(self, dir_list, file=None):
#         file_dir = self.find_files_dirs(dir_list)
#         out = {}
#         if (file_dir) and (file != None) and (file[-1] != '/'):
#             for k, v in file_dir.items():
#                 l = len(self.get_file_name(file))
#                 if l <= len(k) and self.get_file_name(file) == k[:l]:
#                     out[k] = v
#         else:
#             out = file_dir
#         if len(out) == 1 and file == None and (file[-1] != '/'):
#             self.compile_file(list(out.values())[0])
#         self.out = out

#     def matching_opt(self, opt_list):
#         if self.isend():
#             for item in opt_list:
#                 if '-' != item[0]:
#                     self.out[item] = None
#         else:
#             for i in opt_list:
#                 if len(self.last_input()) <= len(i) and self.last_input() == i[:len(self.last_input())]:
#                     self.out[i] = None

#     def getlsspace(self):
#         if len(self.out) == 1 and list(self.out.keys())[0][-1] == '/':
#             return False
#         else:
#             return True

#     def isend(self):  # has space -> true
#         return self.end_dic[self.end]

# # todo 增加同名文件提示和选择
#     def find_files_dirs(self, file_list):
#         file_d = {}
#         for item in file_list:
#             file_d.update(self.find_files(item))   # file_d = {}
#         return file_d

#     def compile_file(self, file):
#         comp = compile.Compile(file)
#         comp.handle()
#         comp.write_args()
#         comp.write_file()
#         return comp.get_options_args()

#     def get_file_path(self, name):
#         for item in self.dir_list:
#             if os.path.isfile(self.root_dir + '/' + item + '/' + name):
#                 return self.root_dir + '/' + item + '/' + name
#         return False

# # todo 设计成字典调用
#     def set_complete(self) -> bool:
#         if self.isend():
#             if self.last_input() == 'hikrun' or self.last_input() == '--code' or self.last_input() == '-c':
#                 dir_list = ["script", 'company']
#                 self.matching_file(dir_list)  # self.matching_file()
#             else:
#                 path = self.get_file_path(self.last_input())
#                 if path:
#                     self.matching_opt(self.compile_file(path))
#                 # file_dir = ["script",'company']
#                 # self.matching_file()  #self.matching_file()
#         else:
#             if '-' in self.last_input():
#                 self.matching_opt(self.hikrun)  # self.matching_file()
#             elif self.last_2_input() == 'hikrun' or self.last_2_input() == '--code' or self.last_2_input() == '--rm':
#                 dir_list = ["script", 'company']
#                 # self.matching_file()
#                 self.matching_file(dir_list, self.last_input())
#             else:
#                 path = self.get_file_path(self.last_2_input())
#                 if path:
#                     self.matching_opt(self.compile_file(path))
#         return self.getlsspace()

class CurFile():
    def __init__(self,script_dir = os.getcwd()):
        self.__file_opt = []
        self.__script_dir = script_dir + '/'
        self.__dic_opt = {
            'all': self.__all,
            'exe_file':self.__isexecutable,
            'alldir':self.__alldir,
            'dir':self.__dir,
        }
    def __find_files(self,postfix='',is_=['all']):
        for root, dirs, files in os.walk(self.__script_dir + postfix):
            for item in is_:
                self.__file_opt = self.__file_opt +  self.__dic_opt[item](dirs,files)
            break
    def __get_dir(self,postfix):
        l = postfix.rfind('/')
        if l < 0:
            return ''
        else:
            return postfix[0:l+1]
    def get_file_opt(self,postfix='',is_=['all']):
        if postfix == None:
            postfix = ''
        else:
            postfix = self.__get_dir(postfix)
        self.__find_files(postfix,is_)
        return self.__file_opt


    def __all(self,dirs,files):
        return files + self.__dir(dirs,files)

    def __isexecutable(self,dirs,files):
        tmp = []
        for file in files:
            if  '.' not in file:
                tmp.append(file)
        return tmp

    def __dir(self,dirs,files):
        r = []
        for d in dirs:
            if d[0] != '.' :
                r.append(d + '/')
        return r
    def __alldir(self,dirs,files):
        r = []
        for d in dirs:
            r.append(d + '/')
        return r

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



class Script(Base):
    def __init__(self,script_dir = ['company','script']):
        super().__init__()
        self.__dir_list = script_dir
        self.__rootdir = os.getenv('HIK_SCRIPT_TOP_DIR')
        self.__root_dir_len = len(self.__rootdir)
    def find_files(self, name='',prefix='/'):
        return CurFile(name).get_file_opt(prefix,is_=['exe_file','dir'])

    def get_script_path(self):
        if not self.isend and '/' in  self.asgs_list[-1] :
            return self.asgs_list[-1]
        else :
            return '/'
# todo 增加同名文件提示和选择
    def find_files_dirs(self):
        self.opt = []
        for item in self.__dir_list:
            self.opt =  self.opt + self.find_files(self.__rootdir + '/' + item + '/',self.get_script_path())  
        return self.opt



    





    # def get_file_path(self, name):
    #     for item in self.dir_list:
    #         if os.path.isfile(self.root_dir + '/' + item + '/' + name):
    #             return self.root_dir + '/' + item + '/' + name
    #     return False



class Code(Script):
    def __init__(self,script_dir = ['company','script']):
        super().__init__(script_dir)

    def run(self):
        pass


class Rm(Script):
    def __init__(self,script_dir = ['company','script']):
        super().__init__(script_dir)

    def run(self):
        pass


class Adb(Base):
    def __init__(self, arg='/'):
        super().__init__(opt=['/'])
        self.arg = arg
        self.sign = ['@']
    def get_default_opt(self):
        l = self.arg.rfind('/')
        if l == -1 :
            self.arg = '/'
        self.files = Shell('adb shell ls -F ' + self.arg[0:l]).exe()
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

class Help():
    def __init__(self):
        pass
    def run(self):
        pass



    
sw_dic = {
    '--code' : Code(),
    '--code-company' : Code(['company']),
    '--code-adb' : Adb,
    '--rm' : Rm(),
    '--rm-company' : Rm(['company']),
    '--git' :  Code(),
}

ws= ['todo','add','show','rm']

class Hikrun(Base):
    def __init__(self):
        super().__init__(list(sw_dic.keys()))
    def get_default_opt(self):
        return Script().find_files_dirs() + ws
        # self.opt.append('-s')
    # def get_opt():
        # self.get_cur_arg() 
    # def run(self):
    #     pass
        

    
def hikrun():
    if  sys.argv[-1] == 'y' :
        if sys.argv[-2] == 'hikrun':
            return Hikrun()
        else :
            return sw_dic[sys.argv[-2]]()
    else :
        if sys.argv[-3] == 'hikrun':
            return Hikrun()
        else :
            return sw_dic[sys.argv[-3]](sys.argv[-2])
        

# def parse_arg():
#     isend = True if sys.argv[-1] == 'y' else False
#     asgs_list = sys.argv[1:-1] if "complete.py" in sys.argv[0] else sys.argv[:-1]
#     if isend :
#         if asgs_list[0] == 'hikrun':




if __name__ == '__main__':
    # Hikrun().run()
    try:
        hikrun().run()
    except :
        pass 
    # com = Complete(sys.argv)
    # com = Complete(['hikrun','test1','y'])
    # com.set_out(com.set_complete())
