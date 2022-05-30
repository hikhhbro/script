import subprocess
import os


class Shell():
    def __init__(self, cmd=''):
        self.cmd = cmd

    def input(self, cmd_str):
        if self.cmd == '':
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
        os.system(self.cmd)
        self.cmd = ''
