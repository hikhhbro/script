import os
import re
import json
class Compile:
    def __init__(self,filepath):
        self.describe = "describe>"
        self.options = "options>"
        self.other = "other"
        self.main = "main"
        self.root_dir = os.getenv('HIK_SCRIPT_TOP_DIR') or os.getenv('SCRIPT_TOP_DIR') or os.getcwd()
        self.filepath = filepath
        self.filedir,self.filename = os.path.split(filepath)
        self.compile_dir = os.path.join(self.root_dir, ".compile", os.path.relpath(filepath, self.root_dir))
        self.outfilepath = os.path.join(self.compile_dir, self.filename)
        self.args_path = os.path.join(self.compile_dir, 'args.json')
        os.makedirs(self.compile_dir, exist_ok=True)
        self.action = ''
        self.writelines=[]
        self.switch = {
            self.describe  :[],
            self.options  :[],
            self.main  :[],
            self.other  :[]
        }
    def get_head(self,action):
        for line in self.switch.get(action):
            if action in line :
                self.switch.get(action).remove(line)
    def get_describe(self):
        out = [self.filename + "_describe () {\n"]
        self.get_head(self.describe)
        for line in  self.switch.get(self.describe):
            s = 'echo "' + line
            s = s[:-1] + '"\n'
            out.append(s)
        out.append("}\n")
        return out

    def __parse_options(self):
        short_opt = []
        long_opt = []
        opt = []
        self.get_head(self.options)
        for line in  self.switch.get(self.options):
            short_opt += ['-' + item for item in re.findall(r'(?<!-)-([A-Za-z])(?![A-Za-z])', line)]
            long_opt += ['--' + item for item in re.findall(r'--([A-Za-z]{2,})', line)]
            text = re.sub(r'-{1,2}[A-Za-z]+', ' ', line)
            opt += re.findall(r'[A-Za-z]+', text)
        return tuple(list(dict.fromkeys(values)) for values in (short_opt, long_opt, opt))

    def get_options(self):
        short_opt, long_opt, opt = self.__parse_options()
        out = [self.filename + '_s_get_options () {\n db="" \n echo "' + ' '.join(short_opt) +'" \n}\n', \
               self.filename + '_l_get_options () {\n db="" \n echo "' + ' '.join(long_opt) +'"  \n}\n', \
               self.filename + '_o_get_options () {\n db="" \n echo "' + ' '.join(opt) +'" \n}\n',      \
               self.filename + '_get_options () {\n db="" \n echo "$(' + self.filename + '_s_get_options) $(' + self.filename  + '_l_get_options) $(' + self.filename + '_o_get_options)" \n}\n']

        return out

    def get_options_args(self):
        out = []
        for values in self.__parse_options():
            out += values
        return list(dict.fromkeys(out))
    def get_main(self):
        out = [] 
        del self.switch.get(self.main)[0]
        for line in self.switch.get(self.main):
            line1 = line.strip()
            line1 = re.sub(' ','',line1)
            if len(line1) > 0 and line1[0] != '#':
                out.append(line)
        self.switch.get(self.main).clear()
        self.switch[self.main] =  out
        s = self.filename + "_probe () {\n"
        self.switch.get(self.main).insert(0,s)
        s = "}\n"
        self.switch.get(self.main).append(s)
        return self.switch.get(self.main)
    def get_action(self,line):
        if self.describe in line :
            self.action = self.describe
        elif self.options in line :
            self.action = self.options
        elif self.action == self.options and line == '!\n':
            self.action = self.main
        else :
            pass
    def handle(self):
        with open(self.filepath) as file:
            for line in file:
                self.get_action(line)
                if self.action in self.switch:
                    self.switch[self.action].append(line)
    def write_file(self):
        with open(self.outfilepath, 'w') as fl:
            fl.writelines(['#!/bin/bash\n'])
            fl.writelines(self.get_describe())
            fl.writelines(self.get_options())
            fl.writelines(self.get_main())
    def write_args(self):
      with open(self.args_path,'w',encoding='utf-8') as file :
        l = json.dumps(self.get_options_args(),ensure_ascii = False)
        file.write(l)


if __name__ == '__main__':
    comp = Compile("/home/hik/private/script/script/get_ip")
    # print(comp.filepath)
    # print(comp.outfilepath)
    comp.handle()
    comp.write_args()
    comp.write_file()
