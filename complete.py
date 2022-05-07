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

    # def isexecutable(self, file):
    #     if '.sh' in file or '.' not in file:
    #         return True
    #     else:
    #         return False

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



class Base():
    def __init__(self, opt=None):
        self.opt = opt or []
        self.opt.append('--help')
        self.setspace = {True: 'compopt +o nospace',
                         False: 'compopt -o nospace'}
        self.out_list = []
        
        self.isend = True if sys.argv[-1] == 'y' else False
        self.asgs_list = sys.argv[1:-1] if "complete.py" in sys.argv[0] else sys.argv[:-1]
    def get_last_input(self):
        if self.isend :
            return None
        return self.asgs_list[-1]
    def get_opt(self, arg):
        if self.isend :
            return self.opt
        for item in self.opt:
            if len(arg) <= len(item) and arg == item[0:len(arg)]:
                self.out_list.append(item)
        return self.out_list

    def set_out(self, out_list):
        print(self.setspace[self.getlsspace()])
        print(' '.join(out_list))
    def getlsspace(self):
        if len(self.out_list) == 0 or (len(self.out_list) == 1 and self.out_list[-1] == '/' or self.out_list[-1] == '='):
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

class Script():
    def __init__(self,script_dir = ['company','script']):
        super().__init__()
        self.__dir_list = script_dir
        self.__rootdir = os.getenv('HIK_SCRIPT_TOP_DIR')
        self.__root_dir_len = len(self.__rootdir)
        self.__dic = {}
    def find_files(self, name=''):
        for root, dirs, files in os.walk(self.__rootdir + name):
            for d in dirs:
                if d[0] != '.':
                    self.__dic['{}/'.format(d)] = root + '/' + d
            for file in files:
                if self.isexecutable(file):
                    self.__dic[file] = root + '/' + file
            break

# todo 增加同名文件提示和选择
    def find_files_dirs(self):
        for item in self.__rootdir:
            __dic.update(self.find_files(item))   # __dic = {}
        return __dic

    





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


class Adb():
    def __init__(self, arg='/'):
        self.arg = arg
        self.sign = ['@']
        l = arg.rfind('/')
        if l == -1:
            l = 0
        self.files = Shell('ls -F ' + arg[l:]).exe()

    def pase(self):
        for i in range(len(self.files)):
            if self.files[i][-1] in self.sign:
                self.files[i] = self.files[i][:-1]

class Help():
    def __init__(self):
        pass
    def run(self):
        pass



    
sw_dic = {
    # None : Script(),
    '--code' : Code(),
    '--code-company' : Code(['company']),
    '--code-adb' : Adb(),
    '--rm' : Rm(),
    '--rm-company' : Rm(['company'])
}


class Hikrun(Base):
    def __init__(self):
        super().__init__(list(sw_dic.keys()))
        # self.opt.append('-s')
    # def get_opt():
        # self.get_cur_arg() 
    # def run(self):
    #     pass
        

    
# def hikrun():
#     if get_cur_arg() == 'hikrun' :
#         return Hikrun()
#     return sw_dic[get_cur()]

def parse_arg():
    isend = True if sys.argv[-1] == 'y' else False
    asgs_list = sys.argv[1:-1] if "complete.py" in sys.argv[0] else sys.argv[:-1]
    while not asgs_list:
        
if __name__ == '__main__':
    Hikrun().run()
    # hikrun().run()
    
    # com = Complete(sys.argv)
    # com = Complete(['hikrun','test1','y'])
    # com.set_out(com.set_complete())
