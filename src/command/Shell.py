import glob
import json
import os
import re
import shlex
import shutil
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


class WindowsShell:
    def __init__(self, config=None, cwd=None):
        self.config = self.__normalize_config(config if config is not None else self.default_config())
        self.cwd = cwd if cwd is not None else self.__windows_cwd()

    def __windows_cwd(self):
        cwd = self.to_wsl_path(self.config.get("cwd", ""))
        if cwd and os.path.isdir(cwd):
            return cwd
        return None

    @classmethod
    def default_config(cls):
        root = os.getenv("SCRIPT_TOP_DIR")
        if not root:
            return {}

        template_path = os.path.join(root, "src", "template", "config", "shell.json")
        config_path = os.path.join(root, "data", "shell", "config.json")
        template = cls.__read_json(template_path)
        config = cls.__read_json(config_path)
        merged = cls.__merge_config(template, config)
        if merged != config:
            cls.__write_json(config_path, merged)
        return merged

    @staticmethod
    def __read_json(path):
        if not os.path.exists(path):
            return {}
        try:
            with open(path, encoding="utf-8") as rf:
                return json.load(rf)
        except Exception as e:
            Log.debug("win shell read config failed %s: %s" % (path, e))
            return {}

    @staticmethod
    def __write_json(path, data):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w+", encoding="utf-8") as wf:
                json.dump(data, wf, indent=1, ensure_ascii=False)
        except Exception as e:
            Log.debug("win shell write config failed %s: %s" % (path, e))

    @classmethod
    def __merge_config(cls, template, config):
        if not isinstance(template, dict):
            return config
        if not isinstance(config, dict):
            return template
        merged = dict(config)
        for key, value in template.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = cls.__merge_config(value, merged[key])
        return merged

    @staticmethod
    def __normalize_config(config):
        if not isinstance(config, dict):
            return {}
        return config.get("windows_shell", config)

    def executable_candidates(self, exe):
        exe_config = self.config.get("executables", {}).get(exe, {})
        out = []
        for item in exe_config.get("candidates", []):
            wsl_item = self.to_wsl_path(item)
            if glob.has_magic(wsl_item):
                out.extend(sorted(glob.glob(wsl_item), reverse=True))
            else:
                out.append(wsl_item)
        return out

    @staticmethod
    def to_wsl_path(path):
        if not path:
            return path
        path = os.path.expanduser(os.path.expandvars(path))
        match = re.match(r"^([a-zA-Z]):[\\/](.*)$", path)
        if not match:
            return path
        drive = match.group(1).lower()
        rest = match.group(2).replace("\\", "/")
        return "/mnt/%s/%s" % (drive, rest)

    @staticmethod
    def to_windows_path(path):
        match = re.match(r"^/mnt/([a-zA-Z])/(.*)$", path)
        if not match:
            return path
        drive = match.group(1).upper()
        rest = match.group(2).replace("/", "\\")
        return "%s:\\%s" % (drive, rest)

    def resolve_exe(self, exe, prefer_config=False):
        path = shutil.which(exe)
        if path:
            Log.debug("win shell resolve %s from PATH: %s" % (exe, path))
            return path
        candidates = self.executable_candidates(exe)
        for item in candidates:
            if os.path.exists(item):
                Log.debug("win shell resolve %s from config: %s" % (exe, item))
                return item
        if prefer_config and candidates:
            Log.debug("win shell resolve %s from first config candidate: %s" % (exe, candidates[0]))
            return candidates[0]
        Log.debug("win shell resolve %s failed, use raw name" % exe)
        return exe

    def resolve_cmd(self, args, sudo=False):
        args = [str(item) for item in args]
        if not args:
            return []
        if os.path.basename(args[0]).lower() == "gsudo.exe":
            sudo = True
            args = args[1:]

        resolved = [self.resolve_exe(args[0], prefer_config=sudo)] + args[1:]
        if sudo:
            gsudo = self.resolve_exe("gsudo.exe")
            resolved = [gsudo, self.to_windows_path(resolved[0])] + resolved[1:]

        Log.debug("win shell cmd: %s" % Shell.format(resolved))
        Log.debug("win shell cwd: %s" % self.cwd)
        return resolved

    def cmd(self, *args, sudo=False):
        return Shell.cmd(*self.resolve_cmd(args, sudo=sudo), cwd=self.cwd)

    def stdout(self, *args, sudo=False):
        return self.cmd(*args, sudo=sudo).stdout()

    def stderr(self, *args, sudo=False):
        return self.cmd(*args, sudo=sudo).stderr()

    def status(self, *args, sudo=False):
        return self.cmd(*args, sudo=sudo).status()

    def powershell(self, script, sudo=False, pwsh=False):
        exe = "pwsh.exe" if pwsh else "powershell.exe"
        return self.cmd(exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script, sudo=sudo)


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
    def win(cls, config=None, cwd=None):
        return WindowsShell(config=config, cwd=cwd)

    @classmethod
    def win_cmd(cls, *args, config=None, cwd=None, sudo=False):
        return cls.win(config=config, cwd=cwd).cmd(*args, sudo=sudo)

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
