import subprocess


class Shell():
    def __init__(self, cmd=''):
        self.cmd = cmd

    def input(self, cmd_str):
        if self.cmd == '':
            self.cmd = cmd_str
        else:
            self.cmd += ' && ' + cmd_str

    def exe(self):
        s = subprocess.Popen(self.cmd, stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE, shell=True)
        stderrinfo, stdoutinfo = s.communicate()
        stderrinfo = None
        return stderrinfo.decode('utf-8')
