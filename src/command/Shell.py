import subprocess
import os
import Log

class Shell():
    def __init__(self, cmd=''):
        self.cmd = cmd
        if self.cmd:
          Log.debug(self.cmd) 

    class Input(object):
        def __init__(self,cmd_str) :
            if self.cmd == '':
                self.cmd = cmd_str
            else:
                self.cmd += ' && ' + cmd_str
                
        def echo(self):
            pass
            
    def input(self, cmd_str):
        Log.debug(cmd_str)
        if cmd_str == '':
            pass
        elif self.cmd == '':
            self.cmd = cmd_str
        else:
            self.cmd += ' && ' + cmd_str
    def input_and_echo(self, cmd_str):
        Log.tips(cmd_str)
        if cmd_str == '':
            pass
        elif self.cmd == '':
            self.cmd = cmd_str
        else:
            self.cmd += ' && ' + cmd_str
    def exe(self,out='out'):
        s = subprocess.Popen(self.cmd, stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE, shell=True)
        stderrinfo, stdoutinfo = s.communicate()
        self.cmd = ''
        if out == 'out':
            return stderrinfo.decode('utf-8')
        elif out == 'err':
            return stdoutinfo.decode('utf-8')

    def exec_system(self):
        status = os.system('/bin/bash -c "%s"' %(self.cmd))
        self.cmd = ''
        return status
        
    def exec_script(self,file,arg):
        arg_str = ""
        for str_ in arg:
            arg_str = arg_str + ' \\\"' + str_ + '\\\"'
        cmd = file + ' ' + arg_str
        Log.debug('/bin/bash -c ' + '\"' + cmd + '\"')
        status = os.system('/bin/bash -c ' + '\"' + cmd + '\"')
        return status