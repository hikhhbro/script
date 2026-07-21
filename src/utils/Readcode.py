import os
from command.Shell import Shell
from command.Base import Base
import Log

class Readcode(Base):
    def __init__(self, args=None):
        super().__init__(args)
        self.meta("根据记录的 import 列表在当前代码树中定位源码文件。", args="<工作名>")
        self.ensure_dir(self.data_dir)
        self.default(self.__code)
        self.file_suffix = '.java'

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
                for line in f.readlines():
                    img_file = line.strip()
                    Log.debug(img_file)
                    file_dic = self.__parse_java_file(img_file)
                    file_set.add(tuple(file_dic.items())[0])
            return [dict([item]) for item in file_set]
            
    def user_file(self,work):
        work_dir = self.data_path(work)
        if os.path.exists(work_dir):
            return os.path.join(work_dir, 'user_file')
        return None
        
    def __get_files(self, file_list):
        if not file_list:
            return []
        keywords = {key for item in file_list for key in item.keys()}
        out = []
        for root, dir_name, file_name in os.walk('./'):
            abs_path = os.path.abspath(root)
            for directory in dir_name:
                if directory in keywords:
                    out.append(os.path.join(abs_path, directory))
            for file in file_name:
                if file in keywords:
                    out.append(os.path.join(abs_path, file))
        return out
    
    def __code(self, arg: list):
        if not arg:
            return
        file_list = self.__parse_file(arg[0])
        files = self.__get_files(file_list)
        if files:
            Shell.code(*files).status()
            
        
    

    def exec(self):
        if not self.args and not self.should_show_help(self.args):
            self.help()
            return
        return self.dispatch(default=self.__code)
