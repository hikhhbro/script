import os
from command.Shell import Shell
from command.Base import Base
from command.Log import Log

class Readcode(Base):
    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.__args_list = args_list or ['']
        self.work_root = self.data_dir + 'readcode/'
        if not  os.path.exists(self.work_root):
            os.mkdir(self.work_root)
        self.option_dic = {
            '': self.__code
        }
        self.file_suffix = '.java'
    def __get_language_file_suffix(self,line):
        tmp_list = list(line)
        Log.debug(tmp_list)
        if not tmp_list:
            return None
        if tmp_list[0] == "import" and tmp_list[-1][-1] == ';' :
            return 'java'
    def __parse_java_file(self,line):
        Log.debug(line)
        split_string = line.split()
        
        while "" in split_string:
            split_string.remove("")
        
        Log.debug(split_string)
        tmp_s = split_string[-1][:-1]
        file = tmp_s.replace('.', '/') + self.file_suffix
        return {os.path.basename(file):file}
            
    def __parse_file(self,work):
        file_set = set()
        if os.path.exists(self.user_file(work)):
            with open(self.user_file(work)) as f:
                # language =  self.__get_language_file_suffix(f.readlines()[0])
                # Log.debug(language)
                for line in f.readlines():
                    img_file = line.strip()
                    Log.debug(img_file)
                    file_dic = self.__parse_java_file(img_file) 
                    file_set.add(file_dic)
            f.close()
            return list(file_set)
            
    def user_file(self,work):
        if os.path.exists(self.work_root + work):
            return self.work_root + work + '/user_file'
        return None
            
    def default_file(self,work):
        if os.path.exists(self.work_root + work):
            return self.work_root + work + '/default_file'
        return None
        
    def __get_files(self,file_list):
        for root,dir_name,file_name in os.walk('./'):
            abs_path = os.path.abspath(root)
            for d in dir_name:
                if keyword in d:
                    print(os.path.join(abs_path,d))
            for f in file_name:
                if keyword in f:
                    print(os.path.join(abs_path,f))
    
    def __code(self, arg: list):
        file_list = self.__parse_file(arg[0])
        files = self.__get_files(file_list)
        # Shell("code %s" %(' '.join(files))).exec_system()
            
        
    

    def exec(self):
        if self.__args_list[0] in self.option_dic.keys():
            self.option_dic[self.__args_list[0]](self.__args_list[1:])
        else:
            self.option_dic[""](self.__args_list[0:])



