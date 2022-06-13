import os
import sys
import compile
from base import Base
import importlib
from hikrun_json import hikrun_json
from trie import Trie
# class Complete:
#     def __init__(self, asgs=[]):
#         self.end = asgs[-1]
#         self.asgs = asgs
#         self.asgs.pop()
#         self.out = {}
#         # self.hikrun = ['--rm', '--code']
#         # self.setspace = {True: 'compopt +o nospace',
#         #                  False: 'compopt -o nospace'}
#         self.end_dic = {'n': False, 'y': True}

#         # self.dir_list = ["script", 'company']

#     def last_input(self):  # hikrun  wiz/w  -> wiz/w
#         return self.asgs[-1]

#     def last_2_input(self):
#         if len(self.asgs) > 1:
#             return self.asgs[-2]
#         else:
#             return None

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





# class Script(Base):
#     def __init__(self,script_dir = ['company','script']):
#         super().__init__()
#         self.__dir_list = script_dir
#         self.__rootdir = os.getenv('HIK_SCRIPT_TOP_DIR')
#         self.__root_dir_len = len(self.__rootdir)
#     def find_files(self, name='',prefix='/'):
#         return CurFile(name).get_file_opt(prefix,is_=['exe_file','dir'])

#     def get_script_path(self):
#         if not self.isend and '/' in  self.asgs_list[-1] :
#             return self.asgs_list[-1]
#         else :
#             return '/'
# # todo 增加同名文件提示和选择
#     def find_files_dirs(self):
#         self.opt = []
#         for item in self.__dir_list:
#             self.opt =  self.opt + self.find_files(self.__rootdir + '/' + item + '/',self.get_script_path())  
#         return self.opt



    





    # def get_file_path(self, name):
    #     for item in self.dir_list:
    #         if os.path.isfile(self.root_dir + '/' + item + '/' + name):
    #             return self.root_dir + '/' + item + '/' + name
    #     return False



# class Code(Script):
#     def __init__(self,script_dir = ['company','script']):
#         super().__init__(script_dir)

#     def run(self):
#         pass


# class Rm(Script):
#     def __init__(self,script_dir = ['company','script']):
#         super().__init__(script_dir)

#     def run(self):
#         pass


# class Adb(Base):
#     def __init__(self, arg='/'):
#         super().__init__(opt=['/'])
#         self.arg = arg
#         self.sign = ['@']
#     def get_default_opt(self):
#         l = self.arg.rfind('/')
#         if l == -1 :
#             self.arg = '/'
#         self.files = Shell('adb shell ls -F ' + self.arg[0:l]).exe()
#         return self.pase()
        
#     def pase(self):
#         out = []
#         file_list = self.files.split('\n')
#         file_list = list(filter(None, file_list))
#         for i in range(len(file_list)):
#             if file_list[i][-1] in self.sign:
#                 out.append(file_list[i][:-1])
#             else :
#                 out.append(file_list[i])
#         return out

# class Help():
#     def __init__(self):
#         pass
#     def run(self):
#         pass



    
# sw_dic = {
#     '--code' : Code(),
#     '--code-company' : Code(['company']),
#     '--code-adb' : Adb,
#     '--rm' : Rm(),
#     '--rm-company' : Rm(['company']),
#     '--git' :  Code(),
# }

# ws= ['todo','add','show','rm']

# class Hikrun(Base):
#     def __init__(self):
#         super().__init__(list(sw_dic.keys()))
#     def get_default_opt(self):
#         return Script().find_files_dirs() + ws
#         # self.opt.append('-s')
#     # def get_opt():
#         # self.get_cur_arg() 
#     # def run(self):
#     #     pass
        

    
# def hikrun():
#     if  sys.argv[-1] == 'y' :
#         if sys.argv[-2] == 'hikrun':
#             return Hikrun()
#         else :
#             return sw_dic[sys.argv[-2]]()
#     else :
#         if sys.argv[-3] == 'hikrun':
#             return Hikrun()
#         else :
#             return sw_dic[sys.argv[-3]](sys.argv[-2])


isend = True if sys.argv[-1] == 'y' else False
asgs_list = sys.argv[1:-1] if "complete.py" in sys.argv[0] else sys.argv[:-1]    
if isend :
    cur = [''] 
else :
    cur = [asgs_list[-1]] 
    del asgs_list[-1]  
def get_class():
    global isend 
    global asgs_list 
    out=asgs_list[0]
    del asgs_list[0]
    if isend :
        if len(asgs_list) > 0:
            out = out + "_" + asgs_list[0]
            del asgs_list[0]
    else :
        if len(asgs_list) > 0:
            out = out + "_" + asgs_list[0]
            del asgs_list[0]
    model = importlib.import_module(out)
    return getattr(model,out)

def get_opname():
    global isend 
    global asgs_list 
    if isend :
        if len(asgs_list) > 0:
            if asgs_list[0][0] != '-':
                return  asgs_list[0]
        else :
            return ''    
    else :
        if len(asgs_list) > 0:
            if asgs_list[0][0] != '-':
                return  asgs_list[0]
        else :
            return ''    

    
        

 
    # def search(self, word):
    #     """
    #     Returns if the word is in the trie.
    #     :type word: str
    #     :rtype: bool
    #     """
    #     curNode = self.root
    #     for c in word:
    #         if not c in curNode:
    #             return False
    #         curNode = curNode[c]
            
    #     # Doesn't end here
    #     if not self.end in curNode:
    #         return False
        
    #     return True
 
    # def startsWith(self, prefix):
    #     """
    #     Returns if there is any word in the trie that starts with the given prefix.
    #     :type prefix: str
    #     :rtype: bool
    #     """
    #     curNode = self.root
    #     for c in prefix:
    #         if not c in curNode:
    #             return False
    #         curNode = curNode[c]
        
    #     return True
 


class Complete():
    def __init__(self,args_list = None):
        self.file = '.complete.json'
        self.trie = Trie(hikrun_json(self.file).read_json())
        self.args = args_list[1:] or []
    
    def get(self):
        return self.trie.search(self.args)

    def set(self):
        if self.trie.insert(self.args) :
            hikrun_json(self.file).write_json(self.trie.root)
        return False
    

if __name__ == '__main__':
    # Hikrun().run()
    # try:
    opt = []
    if len(asgs_list) > 1:
        opt = Complete(asgs_list).get()
    if not opt :
        module = get_class()
        opt = getattr(module(cur), get_opname() + '_opt')()
    Base(opt).run()
    # except :
    #     pass 
    # com = Complete(sys.argv)
    # com = Complete(['hikrun','test1','y'])
    # com.set_out(com.set_complete())
