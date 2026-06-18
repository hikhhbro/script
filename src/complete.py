import os
import sys

sys.path.append(os.getenv('SCRIPT_TOP_DIR')+"/src/command")
from Base import Myclass , Opt
from Listdirs import CurFile
import CompTemp
import types


def get_python_tool_path(name):
    if not name:
        return None
    app_dir = os.getenv('SCRIPT_TOP_DIR') + '/src/utils'
    py_name = name[0].upper() + name[1:] + '.py'
    path = os.path.join(app_dir, py_name)
    if os.path.isfile(path):
        return path
    return None


def get_shell_tool_path(name):
    if not name:
        return None
    return os.path.join(os.getenv('SCRIPT_TOP_DIR'), 'shell', name)


def get_shell_prefix(args_list, isend):
    if isend or not args_list:
        return ''
    arg = args_list[-1]
    index = arg.rfind('/')
    if index < 0:
        return ''
    return arg[:index + 1]


def order_completion_items(out_list, app_list):
    apps = set(app_list)
    py_tools = [item for item in out_list if item in apps]
    dirs = [item for item in out_list if item not in apps and item.endswith('/')]
    shell_tools = [
        item for item in out_list
        if item not in apps and not item.endswith('/')
    ]
    return py_tools + dirs + shell_tools


def print_display_meta(out_list, shell_prefix='', app_list=None):
    app_set = set(app_list or [])
    meta = []
    for item in out_list:
        if not item:
            continue
        shell_item = item if '/' in item else shell_prefix + item
        path = get_shell_tool_path(shell_item)
        if (not path or not os.path.exists(path)) and item in app_set:
            path = get_python_tool_path(item)
        if path and os.path.exists(path):
            meta.append('%s=%s' % (item, path))
    if meta:
        print(' '.join('_display_:' + item for item in meta))

class Complete():
    def __init__(self, opt=None):
        self.opt = opt
        self.setspace = {True: 'compopt +o nospace',
                         False: 'compopt -o nospace'}
        self.out_list = []
        self.default_opt = True
        self.isend = True if sys.argv[-1] == 'y' else False
        self.asgs_list = sys.argv[1:-1] if "complete.py" in sys.argv[0] else sys.argv[:-1]
        self.get_arg_prefix = ''
        
    def get_dic_value(self,dic,key):
        if dic.__contains__(key):
            return  dic[key]
        return  None
    
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
        if self.opt.get_sub_opt() :
            if  self.opt.file_opt:
                return self.opt.get_sub_opt() +  CurFile().get_file_opt(self.get_last_input(True))
            return self.opt.get_sub_opt()
        elif self.opt.file_opt :
            return CurFile().get_file_opt(self.get_last_input(True))
        else :
            return ['']
    def get_opt(self, arg):
        if not arg or arg[-1] =='/':
            r = self.get_default_opt()
            if len(r) ==1 :
                r[0] = self.get_arg_prefix + r[0] 
            return r
        else :
            opt = self.opt.opt_type(arg)
            for item in opt:
                if len(arg) <= len(item) and (self.get_arg_prefix + arg) == item[0:len(self.get_arg_prefix + arg)]:
                    self.default_opt = False
                    self.out_list.append(item)
            if self.default_opt :
                for item in self.get_default_opt():
                    if len(arg) <= len(item) and arg == item[0:len(arg)]:
                        self.out_list.append(self.get_arg_prefix + item)
            return self.out_list

    def set_out(self, out_list):
        print(self.setspace[self.getlsspace()])
        if self.opt.file_opt :
            print("true")
        else :
            print("false")
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

    def run(self):
        self.set_out( self.get_opt(self.get_last_input()))
    

if __name__ == '__main__':
    myclass = Myclass()
    opt = Opt()
    module = myclass.get_class()
    i = 1
    obj = module(myclass.arg.cur)
    method = myclass.get_opname()
    shield = ''
    while method :
        f = getattr(obj, method + '_opt',None)
        if not f:
          shield = method
          i = i+1
          method = myclass.get_opname(i)
        else :
          break
    f = getattr(obj, method + '_opt',None)
    opt = f()
    if shield :
      opt.retreat = shield
      opt.shield_opt()
    complete = Complete(opt)
    out_list = complete.get_opt(complete.get_last_input())
    app_list = obj._get_app() if hasattr(obj, '_get_app') else []
    if app_list:
        out_list = order_completion_items(out_list, app_list)
        complete.out_list = out_list
    complete.set_out(out_list)
    if not opt.file_opt:
        print_display_meta(out_list, get_shell_prefix(complete.asgs_list, complete.isend), app_list)
    # 输出 Python 工具名作为颜色显示元数据。
    # 仅在真正顶层补全时输出，避免子命令路径被误判。
    asgs = sys.argv[1:-1]
    top_level = len(asgs) == 1
    if len(asgs) == 2 and hasattr(obj, '_get_app'):
        import CompTemp
        known_py = set(obj._get_app())
        shell_dir = os.getenv('SCRIPT_TOP_DIR') + '/shell'
        if not (
            CompTemp.CompTemp().get(asgs[1])
            or asgs[1] in known_py
            or os.path.exists(os.path.join(shell_dir, asgs[1]))
        ):
            top_level = True
    if top_level and hasattr(obj, '_get_app'):
        print(' '.join('_py_:' + item for item in obj._get_app()))
