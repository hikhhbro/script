import os
import sys
import subprocess

class Shell():
    def __init__(self):
        self.cmd = ''
    def input(self,cmd_str):
        if self.cmd == '' :
            self.cmd = cmd_str
        else :
            self.cmd += ' && ' + cmd_str
    def get_cmd(self):
        return self.cmd
    def exe(self):
        s = subprocess.Popen(str(self.cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        stderrinfo, stdoutinfo = s.communicate()
        return s.returncode
    
root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
dir_list = ["script",'company'] 
def get_file_path(file) :
    for item in dir_list:
        if os.path.isfile(root_dir + '/'+ item + '/'+ file):
            return root_dir + '/'+ item + '/'+ file
    return None

def get_compile_path(file) :
    for item in dir_list:
        if os.path.isfile(root_dir + '/'+ '.compile/' + item + '/'+ file):
            return root_dir + '/'+ '.compile/' + item + '/'+ file
    return None
    

def execute(cmd):
    s = subprocess.Popen(str(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    stderrinfo, stdoutinfo = s.communicate()
    return s.returncode

def execute_file(file,arg_list):
    arg_str = ' '.join(arg_list)
    path = get_file_path(file)
    if path == None :
        return False
    return execute('. ' + path + '&&' + file + '_probe' + arg_str)


def company_file(args_list):
    args_list.pop(0)
    file =  root_dir + '/'+ 'company/' + ''.join(args_list[-1])
    if os.path.isfile(file) :
        execute('code '+ file)
    else:
        cmd = 'cp ' +  root_dir + '/' + '.template ' + file 
        cmd += "&& code " + file
        execute(cmd)
def script_file(args_list):
    file =  root_dir + '/'+ 'script/' + ''.join(args_list[-1])
    if os.path.isfile(file) :
        execute('code '+ file)
    else:
        cmd = 'cp ' +  root_dir + '/' + '.template ' + file 
        cmd += "&& code " + file
        execute(cmd)

def adb_dest_file(file):
    return file.replace('/','#')
def adb_src_file(file):
    return file.replace('#','/')

def adb_file(args_list):
    srcfile = ''.join(args_list[-1])
    dire = root_dir + '/adb_file/' + adb_dest_file(srcfile)
    s = Shell()
    s.input('adb pull '+ srcfile + ' ' + dire)
    s.input('code ' + dire)
    s.exe()
def adb_sync_file(args_list):
    s = Shell()
    for root, dirs, files in os.walk(root_dir + '/adb_file/'):
        s.input('adb push '+ root + '/' + files[0] + ' ' + adb_src_file(files[0]))
        s.input('rm  '+ root + '/' + files[0])
        s.exe()
        break

file_run = {
    '-c' : company_file,
    '-a' : adb_file, 
    '-adb-sync' :adb_sync_file,
    None : script_file
}


def code(args_list):
    if args_list[0] in file_run :
        file_run[args_list[0]](args_list[1:])
    else :
        file_run[None](args_list)
        
def rm(args_list):
    if args_list[0] == '-c' :
        args_list.pop(0)
        file =  root_dir + '/'+ 'company/' + ''.join(args_list[-1])
        resycle =  root_dir + '/'+ 'company/.resycle/' + ''.join(args_list[-1])
        execute('mv '+ file + ' ' + resycle)
    else :
        file =  root_dir + '/'+ 'script/' + ''.join(args_list[-1])
        resycle =  root_dir + '/'+ 'script/.resycle/' + ''.join(args_list[-1])
        execute('mv '+ file + ' ' + resycle)


run = { 
 '--code' : code,
 '--rm' : rm
      }

  

def main():
    for i in range(len(sys.argv)):
        if sys.argv[i] in list(run.keys()) :
            run[sys.argv[i]](sys.argv[i+1:])
            break
    
if __name__ == '__main__':
    main()