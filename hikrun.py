import os
import sys
import time
import copy
from shell import Shell
import subprocess
from hikrun_json import hikrun_json
root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
dir_list = ["script", 'company']


class Code():
    def __init__(self, args=None):
        self.__dic = {
            '-c': self.__company_file,
            '-adb': self.__adb_file,
            '-adb-sync': self.__adb_sync_file,
            None: self.__open_file
        }
        
        self.__args_list = args or []

    def __code_file(self, f):
        if os.path.isfile(f):
            Shell('code ' + f).exe()

        s = Shell()
        s.input('cp ' + root_dir + '/' + '.template ' + f)
        s.input("code " + f)
        s.exe()

    def __company_file(self, args_list):
        f = root_dir + '/' + 'company/' + ''.join(args_list[-1])
        self.__code_file(f)

    def __script_file(self, args_list):
        f = root_dir + '/' + 'script/' + ''.join(args_list[-1])
        self.__code_file(f)

    def __find_file(self, args_list):
        for item in dir_list:
            f = root_dir + '/' + item + '/' + args_list[-1]
            if os.path.isfile(f):
                return f

    def __open_file(self, args_list):
        f = self.__find_file(args_list)
        if f:
            self.__code_file(f)
        else:
            self.__script_file(args_list)

    def __adb_dest_file(self, f):
        return f.replace('/', '#')

    def __adb_src_file(self,f):
        return f.replace('#', '/')

    def __adb_file(self, args_list):
        srcfile = ''.join(args_list[-1])
        dire = root_dir + '/adb_file/' + self.__adb_dest_file(srcfile)
        s = Shell()
        s.input('adb root')
        s.input('adb remount')
        s.input('adb disable-verity')
        s.input('adb pull ' + srcfile + ' ' + dire)
        s.input('code ' + dire)
        s.exec_system()
        a = input("是否保存至手机: 回车")
        s.input('adb push ' + dire + ' ' + srcfile )
        s.exec_system()


    def run(self):
        if self.__args_list[0] in self.__dic:
            self.__dic[self.__args_list[0]](self.__args_list[1:])
        else:
            self.__dic[None](self.__args_list)


class Rm():
    def __init__(self, args_list=None):
        self.__args_list = args_list or []

    def run(self):
        if self.__args_list[0] == '-c':
            self.__args_list.pop(0)
            dir_tmp = 'company/'
        else:
            dir_tmp = 'script/'
        f = root_dir + '/' + dir_tmp + ''.join(self.__args_list[-1])
        resycle = root_dir + '/' + dir_tmp + \
            '.resycle/' + ''.join(self.__args_list[-1])
        Shell('mv ' + f + ' ' + resycle).exe()

class Git():
    def __init__(self, args_list=None):
        self.__args_list = args_list or []
        self.add_dic = { }
    def __find_git(self):
        return  True if Shell('git rev-parse --is-inside-work-tree').exe() == 'true\n' else False
    def __get_path(self):
        return Shell('pwd').exe()[:-1]

    def __get_remote(self):
        return Shell('git remote -v').exe().split('\n')[0]
    def __get_branch(self):
        return Shell("git branch | sed -n '/\* /s///p'").exe()[:-1]


    def add(self):
        if self.__find_git():
            self.add_dic =  {self.__get_path():[self.__get_remote(),self.__get_branch()]}
    def print_add(self):
        for key, value in self.add_dic.items():
            # print(key,value[0],value[1])
            print("本地: %s |远程:%s | 分支: %s" % (key,value[0],value[1]))
    
    def run(self):
        if self.__args_list[-1] == 'add' :
            self.add()
            self.print_add()

class Todo():
    def __init__(self, args_list=None):
        self.__args_list = args_list or []
        self.todo_dic = { }
        self.option_dic = {
            'add' : self.add,
            'rm' : self.rm,
            'show' : self.show,
        }

    def __write_json(self,text):
        with open("%s/todo/todo_list.json" % (root_dir)) as rf:
            json_data = json.load(rf)
        if not json_data.__contains__(time.strftime("%Y/%m/%d")):
            json_data[time.strftime("%Y/%m/%d")] = [text]
        else :
            json_data[time.strftime("%Y/%m/%d")].append(text)
        with open("%s/todo/todo_list.json" % (root_dir), "w+") as wf:
            js = json.dumps(json_data,indent=1)
            wf.write(js)
    def __read_json(self):    
        with open("%s/todo/todo_list.json" % (root_dir)) as rf:
            json_data = json.load(rf)
        return json_data

    def __add_gitlab(self,commit):
        Shell('cd %s/todo/ && git add todo/todo_list.json && git commit -m %s' %(root_dir,commit) ).exe()
        
    def __text(self,text:list):
        return ' '.join(text)
    
    def add(self,text):
        if text:
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
        with open("%s/todo/todo_list.json" % (root_dir), "w+") as wf:
            js = json.dumps(txt_dic,indent=1)
            wf.write(js)
            self.__add_gitlab("rm todo")


    def run(self):
        self.option_dic[self.__args_list[0]](self.__args_list[1:]) 

class Cd():
    def __init__(self, args_list=None):
        self.__args_list = args_list or []
        self.add_dic = { }

    def __quote_against_shell_expansion(self,s):
        import pipes
        return pipes.quote(s)

    def __put_text_back_into_terminal_input_buffer(self,text):
        import fcntl, termios
        for c in text:
            fcntl.ioctl(1, termios.TIOCSTI, c)

    def __change_parent_process_directory(self,dest):
        self.__put_text_back_into_terminal_input_buffer("cd "+ self.__quote_against_shell_expansion(dest)+"\n")

    def exec(self):
        if self.__args_list[-1][0] == '/':
            dir_prefix = ''
        else :
            dir_prefix = os.getcwd() + '/'
        self.__change_parent_process_directory(dir_prefix + self.__args_list[-1] )


run = {
    '--code': lambda args_list:  Code(args_list).run(),
    '--rm': lambda args_list: Rm(args_list).run(),
    '--git':lambda args_list: Git(args_list).run(),
    'todo':lambda args_list: Todo(args_list).run(),
    'adb':lambda args_list: Adb(args_list).exec(),
    'cd':lambda args_list: Cd(args_list).exec(),
}


def get_probe(f):
    index = f.rfind('/')
    if index != -1:
        return f[index+1:] + '_probe'
    return f + '_probe'


def get_file_path(f):
    for item in dir_list:
        if os.path.isfile(root_dir + '/' + item + '/' + f):
            return root_dir + '/' + item + '/' + f
    return None


def get_compile_path(f):
    for item in dir_list:
        if os.path.isfile(root_dir + '/' + '.compile/' + item  + '/' + f):
            return root_dir + '/' + '.compile/' + \
                item  + '/' + f


class hikrun(hikrun_json):
    def __init__(self, args_list=None):
        super().__init__('.complete.json')
        self.__args_list = args_list or []
        
    def _opt(self):
        return list(self.read_json().keys())

def main():
    if 'hikrun.py' in  sys.argv[0] :
        del sys.argv[0]
    if sys.argv[-1]  in ['n','y']:
        del sys.argv[-1]
    if sys.argv[1] in list(run.keys()):
        run[sys.argv[1]](sys.argv[2:])
    elif sys.argv[1][0:sys.argv[1].rfind('-')] in list(run.keys()):
        tmp_cmd = [sys.argv[1][sys.argv[1].rfind('-'):]] + sys.argv[2:]
        run[sys.argv[1][0:sys.argv[1].rfind('-')]](tmp_cmd)
    else:
        s = Shell()
        f = get_compile_path(sys.argv[1])
        s.input('source ${HIK_SCRIPT_TOP_DIR}/base.sh')
        s.input('. ' + f)
        s.input(get_probe(sys.argv[1]) + ' ' + ''.join(sys.argv[2:]))
        s.exec_system()


if __name__ == '__main__':
    main()
