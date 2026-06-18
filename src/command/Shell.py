import os
import shlex
import subprocess
import Log


class Shell():
    def __init__(self, cmd=''):
        self.cmd = cmd
        if self.cmd:
            Log.debug(self.cmd)

    def input(self, cmd_str):
        Log.debug(cmd_str)
        if not cmd_str:
            return
        if self.cmd == '':
            self.cmd = cmd_str
        else:
            self.cmd += ' && ' + cmd_str

    def input_and_echo(self, cmd_str):
        Log.tips(cmd_str)
        self.input(cmd_str)

    def exe(self, out='out'):
        if not self.cmd:
            return ''
        process = subprocess.Popen(
            self.cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=True,
            text=True,
        )
        stdoutinfo, stderrinfo = process.communicate()
        self.cmd = ''
        if out == 'out':
            return stdoutinfo
        elif out == 'err':
            return stderrinfo
        return stdoutinfo

    def exec_system(self):
        if not self.cmd:
            return 0
        status = subprocess.call(['/bin/bash', '-lc', self.cmd])
        self.cmd = ''
        return status

    def exec_script(self, file, arg):
        cmd = shlex.quote(file)
        for item in arg:
            cmd += ' ' + shlex.quote(item)
        Log.debug('/bin/bash -lc ' + repr(cmd))
        return subprocess.call(['/bin/bash', '-lc', cmd])
