import os
from command.Shell import Shell
from command.Base import Base
import Log

class Readcode(Base):
    help_summary = "根据记录的 import 列表在当前代码树中定位源码文件。"
    help_usage = "{tool_name} readcode <工作名>"
    help_options = {
        "--help": "显示当前帮助",
    }
    help_examples = [
        "hikrun readcode demo",
    ]

    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.__args_list = self.args
        self.work_root = self.data_path('readcode') + '/'
        self.ensure_dir(self.work_root)
        self.set_commands({
            '': self.__code
        })
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
                    file_set.add(tuple(file_dic.items())[0])
            return [dict([item]) for item in file_set]
            
    def user_file(self,work):
        if os.path.exists(self.work_root + work):
            return self.work_root + work + '/user_file'
        return None
            
    def default_file(self,work):
        if os.path.exists(self.work_root + work):
            return self.work_root + work + '/default_file'
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
        if not self.__args_list and not self.should_show_help(self.__args_list):
            self.help()
            return
        return self.dispatch(self.__args_list, default=self.option_dic[""])

