import subprocess
class Shell():
    def __init__(self,cmd=''):
        self.cmd = cmd
        self.cmd = cmd
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
        return stderrinfo.decode('utf-8')