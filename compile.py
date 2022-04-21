import os
import re
class Compile:
    def __init__(self,filepath):
        self.describe = "describe>"
        self.options = "options>"
        self.other = "other"
        self.main = "main"
        self.root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
        self.root_dir_len = len(self.root_dir)
        self.filepath = filepath
        self.outfilepath = self.root_dir +  "/.compile/"+ filepath[self.root_dir_len+1:]
        self.filedir,self.filename = os.path.split(filepath)
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
    def get_options(self):
        tmp = []
        short_opt = ''
        long_opt = ''
        opt = ''
        self.get_head(self.options)
        for line in  self.switch.get(self.options):
            s_list = list(line)
            i = 0 
            while (i < len(s_list)):
                if s_list[i] == '-':
                    if s_list[i+1].isalpha() and s_list[i+2].isalpha() == False:
                            short_opt = '-' + s_list[i+1] + ' ' + short_opt
                            i = i+1
                    else :
                        if s_list[i+1] == '-' and s_list[i+2].isalpha() and s_list[i+3].isalpha():
                            long_opt = long_opt + ' --' +  s_list[i+2]
                            i = i+3
                            try:
                                while  s_list[i].isalpha():
                                    long_opt = long_opt +  s_list[i]
                                    i = i+1
                            except:  
                                break
                else:
                    tmp.append(s_list[i])
                i = i+1
            stmp = ''.join(tmp)
            stmp = re.sub('[^a-zA-Z]', ' ', stmp)
            if stmp.strip():
                opt = stmp.strip() + opt
            tmp.clear()
        out = [self.filename + '_s_get_options () {\n db="" \n echo "' + short_opt +'" \n}\n', \
               self.filename + '_l_get_options () {\n db="" \n echo "' + long_opt +'"  \n}\n', \
               self.filename + '_o_get_options () {\n db="" \n echo "' + opt +'" \n}\n',      \
               self.filename + '_get_options () {\n db="" \n echo "$(' + self.filename + '_s_get_options) $(' + self.filename  + '_l_get_options) $(' + self.filename + '_get_options)" \n}\n']

        return out
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
        file = open(self.filepath) 
        for line in file:
            self.get_action(line)
            if self.action in self.switch.keys() :
                self.switch.get(self.action).append(line)
            else :
                pass
        file.close()
    def write_file(self):
        fl=open(self.outfilepath, 'a')
        fl.seek(0)
        fl.truncate()
        fl.writelines(['#!/bin/bash\n'])
        fl.writelines(self.get_describe())
        fl.writelines(self.get_options())
        fl.writelines(self.get_main())
        fl.close()



if __name__ == '__main__':
    comp = Compile("/home/hik/script/script/test1")
    # print(comp.filepath)
    # print(comp.outfilepath)
    comp.handle()
    comp.write_file()