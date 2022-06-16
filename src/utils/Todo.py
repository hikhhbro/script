import json
import time
import os
from command.Shell import Shell
import copy
class Todo():
    def __init__(self, args_list=None):
        self.root_dir = os.getenv('SCRIPT_TOP_DIR')
        self.__args_list = args_list or []
        self.todo_dic = { }
        self.option_dic = {
            'add' : self.add,
            'rm' : self.rm,
            'show' : self.show,
        }
        self.todo_dir = self.root_dir + '/data/todo/'
        self.todo_file = self.todo_dir + 'todo_list.json'
        if not os.path.exists(self.todo_file):
            Shell('mkdir -p '+ self.todo_dir + "&& echo '{}'> %s" %(self.todo_file)).exec_system()
    def __write_json(self,text):
        with open("%s" % (self.todo_file)) as rf:
            json_data = json.load(rf)
        if not json_data.__contains__(time.strftime("%Y/%m/%d")):
            json_data[time.strftime("%Y/%m/%d")] = [text]
        else :
            json_data[time.strftime("%Y/%m/%d")].append(text)
        with open("%s" % (self.todo_file), "w+") as wf:
            js = json.dumps(json_data,indent=1)
            wf.write(js)
    def __read_json(self):    
        with open("%s" % (self.todo_file)) as rf:
            json_data = json.load(rf)
        return json_data
    def __init_git(self):
        git_remote = input("请输出远程仓库地址: ")
        Shell('cd %s && git init  &&git remote add orgin %s' %(self.todo_dir,git_remote) ).exe()
    def __add_gitlab(self,commit):
        if not os.path.exists(self.todo_dir + '.git'):
            print("此目录任不是git仓库，请初始化")
            self.__init_git()
            return
        Shell('cd %s && git add . && git commit -m %s' %(self.todo_dir,commit) ).exe()
        
    def __text(self,text:list):
        return ' '.join(text)
    
    def add(self,text):
        if text:
            start = text.index('-c')
            if start >= 0:
                c = Shell(text[start:]).exe().replace('\n','')
                del text[start:]
                text.append(c)
            self.__write_json(self.__text(text))
            self.__add_gitlab("add todo")
    def show(self,serial:list):
        txt_dic = self.__read_json()
        prefix_i = 0
        if not txt_dic.__contains__(' '.join(serial)):
            for k,v in txt_dic.items():
                print("\033[1;34m   %s\033[0m" % k)
                for i in range(len(v)):
                    print("%s: %s" %(prefix_i,v[i]))
                    prefix_i = prefix_i + 1
        else :
            print("\033[1;34m   %s\033[0m" % ' '.join(serial))
            for i in range(len(txt_dic[' '.join(serial)])):
                print("%s: %s" %(i,txt_dic[' '.join(serial)][i]))
    def __get_rm_serial(self,serial:list):
        r = {
            "time" : [],
            "serial":[]
        }
        for item in serial:
            if '/' in item:
                r["time"].append(item)
            else:
                if ':' in item:
                    sp = item.find(':')
                    start = int(item[0:sp])
                    end = int(item[sp+1:])
                    r["serial"] = r["serial"] + list(range(start,end+1))
                else :
                    r["serial"].append(int(item))
        r["serial"] = list(set(r["serial"]))
        r["serial"].sort()
        return r
                
    def rm(self,serial:list):
        txt_dic = self.__read_json()
        s = self.__get_rm_serial(serial)
        prefix_i = 0
        txt_dic_t = copy.deepcopy(txt_dic)
        for k,v in txt_dic_t.items():
            i_r=0
            for i in range(len(v)):
                if s["serial"]:
                    if prefix_i in s["serial"]:
                        del txt_dic[k][i-i_r]
                        i_r = i_r + 1
                        if not txt_dic[k]:
                            txt_dic.pop(k)
                        s["serial"].remove(prefix_i)
                        if not s["serial"]:
                            break
                    prefix_i = prefix_i + 1
            else:
                continue
            break
        with open("%s" % (self.todo_file), "w+") as wf:
            js = json.dumps(txt_dic,indent=1)
            wf.write(js)
            self.__add_gitlab("rm todo")

    def _opt(self):
        return list(self.option_dic.keys())
    def add_opt(self):
        if self.__args_list[-1][0] == '-':
            return ['-c']
        return []
    def exec(self):
        self.option_dic[self.__args_list[0]](self.__args_list[1:]) 