import shlex
import subprocess

import Log


class ShellResult:
    def __init__(self, process):
        self.process = process
        self.stdout = process.stdout or ''
        self.stderr = process.stderr or ''
        self.returncode = process.returncode

    def out(self):
        return self.stdout

    def err(self):
        return self.stderr

    def status(self):
        return self.returncode

    def ok(self):
        return self.returncode == 0


class ShellChain:
    def __init__(self, cwd=None, echo=False):
        self.cwd = cwd
        self.echo = echo
        self.steps = []

    def cmd(self, *args):
        self.steps.append(('cmd', args))
        return self

    def git(self, *args):
        return self.cmd('git', *args)

    def mkdir(self, path):
        return self.cmd('mkdir', '-p', path)

    def bash(self, script):
        self.steps.append(('bash', script))
        return self

    def __run_step(self, kind, payload, capture):
        if kind == 'cmd':
            return Shell.cmd(*payload, cwd=self.cwd).run(capture)
        return Shell.bash(payload, cwd=self.cwd).run(capture)

    def run(self, capture=False):
        last = ShellResult(subprocess.CompletedProcess([], 0, '', ''))
        for kind, payload in self.steps:
            if self.echo:
                Log.tips(Shell.format(payload) if kind == 'cmd' else payload)
            result = self.__run_step(kind, payload, capture)
            if result.status() != 0:
                return result
            last = result
        return last

    def status(self):
        return self.run(False).status()

    def stdout(self):
        return self.run(True).out()


class ShellSession:
    def __init__(self, cwd=None, echo=False):
        self.cwd = cwd
        self.echo = echo
        self.lines = []

    def cmd(self, *args):
        return self.bash(Shell.format(args))

    def git(self, *args):
        return self.cmd('git', *args)

    def mkdir(self, path):
        return self.cmd('mkdir', '-p', path)

    def bash(self, script):
        if script:
            if self.echo:
                Log.tips(script)
            Log.debug(script)
            self.lines.append(script)
        return self

    def run(self, capture=False):
        return Shell.bash(' && '.join(self.lines), cwd=self.cwd).run(capture)

    def status(self):
        return self.run(False).status()

    def stdout(self):
        return self.run(True).out()


class Shell:
    def __init__(self, cmd='', cwd=None):
        self.cwd = cwd
        self.steps = []
        self.argv = None
        self.script = None
        if cmd:
            self.input(cmd)

    @classmethod
    def cmd(cls, *args, cwd=None):
        shell = cls(cwd=cwd)
        shell.argv = [str(item) for item in args]
        shell.script = None
        return shell

    @classmethod
    def bash(cls, script, cwd=None):
        shell = cls(cwd=cwd)
        shell.argv = None
        shell.script = script
        return shell

    @classmethod
    def chain(cls, cwd=None, echo=False):
        return ShellChain(cwd=cwd, echo=echo)

    @classmethod
    def session(cls, cwd=None, echo=False):
        return ShellSession(cwd=cwd, echo=echo)

    @classmethod
    def git(cls, cwd, *args):
        return cls.cmd('git', *args, cwd=cwd)

    @classmethod
    def mkdir(cls, path):
        return cls.cmd('mkdir', '-p', path)

    @classmethod
    def code(cls, *paths, wait=False):
        args = ['code']
        if wait:
            args.append('-w')
        args.extend(paths)
        return cls.cmd(*args)

    @staticmethod
    def format(args):
        return ' '.join(shlex.quote(str(item)) for item in args)

    def input(self, cmd_str):
        if cmd_str:
            Log.debug(cmd_str)
            self.steps.append(cmd_str)
        return self

    def input_and_echo(self, cmd_str):
        Log.tips(cmd_str)
        return self.input(cmd_str)

    @property
    def cmd_text(self):
        if hasattr(self, 'argv') and self.argv is not None:
            return self.format(self.argv)
        if hasattr(self, 'script') and self.script is not None:
            return self.script
        return ' && '.join(self.steps)

    def clear(self):
        self.steps = []
        self.argv = None
        self.script = None

    def run(self, capture=False):
        if not self.cmd_text:
            return ShellResult(subprocess.CompletedProcess([], 0, '', ''))

        if hasattr(self, 'argv') and self.argv is not None:
            cmd = self.argv
            Log.debug(self.format(cmd))
            shell = False
        else:
            cmd = ['/bin/bash', '-lc', self.cmd_text]
            Log.debug('/bin/bash -lc ' + repr(self.cmd_text))
            shell = False

        kwargs = {'cwd': self.cwd, 'text': True}
        if capture:
            kwargs.update({'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE})

        try:
            return ShellResult(subprocess.run(cmd, shell=shell, **kwargs))
        finally:
            self.clear()

    def stdout(self):
        return self.run(True).out()

    def stderr(self):
        return self.run(True).err()

    def status(self):
        return self.run(False).status()

    def exe(self, out='out'):
        result = self.run(True)
        if out == 'err':
            return result.err()
        if out == 'status':
            return result.status()
        return result.out()

    def exec_system(self):
        return self.status()

    def exec_script(self, file, arg):
        return Shell.cmd(file, *arg, cwd=self.cwd).status()
