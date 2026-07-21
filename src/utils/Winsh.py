import os
import re
import shlex
import shutil
import subprocess
import sys
import glob

import Log
from command.Base import Base, Opt


class Winsh(Base):
    help_summary = "从 WSL 调用 Windows 侧命令，并提供常用工具的分层补全。"
    help_usage = "{tool_name} winsh <windows工具> [子命令|参数]"
    help_options = {
        "usbipd": "管理 Windows USB/IP 设备并连接到 WSL",
        "--sudo": "强制使用 gsudo.exe 提权执行后续 Windows 命令",
        "--help": "显示当前帮助",
    }
    help_examples = [
        "hikrun winsh usbipd list",
        "hikrun winsh usbipd bind --busid 2-1",
        "hikrun winsh usbipd attach --wsl --busid 2-1",
    ]

    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.__args_list = self.args
        self.winsh_config = self.__load_winsh_config()
        self.windows_tools = {
            "usbipd": {
                "exe": "usbipd.exe",
                "subcommands": {
                    "list": ["--usbids", "--parsable"],
                    "state": [],
                    "bind": ["--busid", "--force"],
                    "unbind": ["--busid", "--force"],
                    "attach": ["--busid", "--wsl", "--distribution", "--auto-attach"],
                    "detach": ["--busid"],
                },
                "admin_subcommands": {"bind", "unbind"},
                "value_options": {
                    "--busid": self.__usbipd_busids,
                    "--distribution": self.__wsl_distros,
                },
            },
        }
        self.set_commands({
            "usbipd": self.__run_usbipd,
        })
        Log.debug("winsh args: %s" % self.__args_list)
        Log.debug("winsh tools: %s" % list(self.windows_tools.keys()))

    def __load_winsh_config(self):
        template_path = os.path.join(self.tool_dir, "src", "template", "config", "winsh.json")
        template = {}
        if os.path.exists(template_path):
            try:
                from command.Json import Json
                template = Json(template_path).read()
            except Exception as e:
                Log.debug("winsh read template config failed: %s" % e)
        try:
            config = self.config.read(template)
        except Exception:
            config = template
        if template and not config:
            self.config.write(template)
            config = template
        Log.debug("winsh config: %s" % config)
        return config or {}

    def __windows_cwd(self):
        cwd = self.__to_wsl_path(self.winsh_config.get("windows_cwd", ""))
        if os.path.isdir(cwd):
            return cwd
        return None

    def __exe_candidates(self, exe):
        exe_config = self.winsh_config.get("executables", {}).get(exe, {})
        out = []
        for item in exe_config.get("candidates", []):
            wsl_item = self.__to_wsl_path(item)
            if glob.has_magic(wsl_item):
                out.extend(sorted(glob.glob(wsl_item), reverse=True))
            else:
                out.append(wsl_item)
        return out

    def __to_wsl_path(self, path):
        if not path:
            return path
        path = os.path.expanduser(os.path.expandvars(path))
        match = re.match(r"^([a-zA-Z]):[\\/](.*)$", path)
        if not match:
            return path
        drive = match.group(1).lower()
        rest = match.group(2).replace("\\", "/")
        return "/mnt/%s/%s" % (drive, rest)

    def __resolve_exe(self, exe):
        path = shutil.which(exe)
        if path:
            Log.debug("winsh resolve %s from PATH: %s" % (exe, path))
            return path
        for item in self.__exe_candidates(exe):
            if os.path.exists(item):
                Log.debug("winsh resolve %s from candidate: %s" % (exe, item))
                return item
        Log.debug("winsh resolve %s failed" % exe)
        return exe

    def __to_windows_path(self, path):
        match = re.match(r"^/mnt/([a-zA-Z])/(.*)$", path)
        if not match:
            return path
        drive = match.group(1).upper()
        rest = match.group(2).replace("/", "\\")
        win_path = "%s:\\%s" % (drive, rest)
        Log.debug("winsh path to windows: %s -> %s" % (path, win_path))
        return win_path

    def __resolve_cmd(self, cmd):
        if not cmd:
            return cmd
        resolved = [self.__resolve_exe(cmd[0])] + cmd[1:]
        if os.path.basename(cmd[0]).lower() == "gsudo.exe" and len(cmd) > 1:
            resolved[1] = self.__to_windows_path(self.__resolve_exe(cmd[1]))
        Log.debug("winsh resolved cmd: %s" % " ".join(shlex.quote(item) for item in resolved))
        return resolved

    def __run(self, cmd):
        cmd = self.__resolve_cmd(cmd)
        Log.debug("winsh probe cmd: %s" % " ".join(shlex.quote(item) for item in cmd))
        Log.debug("winsh windows cwd: %s" % self.__windows_cwd())
        try:
            out = subprocess.check_output(
                cmd,
                stderr=subprocess.DEVNULL,
                text=True,
                cwd=self.__windows_cwd(),
            )
        except Exception as e:
            Log.debug("winsh probe failed: %s" % e)
            return ""
        Log.debug("winsh probe output: %s" % out)
        return out

    def __usbipd_busids(self):
        out = self.__run(["usbipd.exe", "list"])
        busids = []
        for line in out.splitlines():
            match = re.match(r"^\s*([0-9]+-[0-9]+)\s+", line)
            if match:
                busids.append(match.group(1))
        Log.debug("winsh usbipd busids: %s" % busids)
        return busids

    def __wsl_distros(self):
        out = self.__run(["wsl.exe", "-l", "-q"])
        distros = []
        for line in out.splitlines():
            name = line.replace("\x00", "").strip()
            if name:
                distros.append(name)
        Log.debug("winsh wsl distros: %s" % distros)
        return distros

    def completion_root_options(self):
        return {"--sudo": None}

    def completion_spec(self):
        return {
            "usbipd": {
                "_commands": {
                    "list": {"_options": {"--usbids": None, "--parsable": None}},
                    "state": {},
                    "bind": {"_options": {"--busid": self.__usbipd_busids, "--force": None}},
                    "unbind": {"_options": {"--busid": self.__usbipd_busids, "--force": None}},
                    "attach": {"_options": {
                        "--busid": self.__usbipd_busids,
                        "--wsl": None,
                        "--distribution": self.__wsl_distros,
                        "--auto-attach": None,
                    }},
                    "detach": {"_options": {"--busid": self.__usbipd_busids}},
                }
            }
        }

    def __run_windows_tool(self, tool_name, args):
        tool = self.windows_tools.get(tool_name)
        if not tool:
            Log.error("未知 Windows 工具: %s" % tool_name)
            return 1

        Log.debug("winsh run tool=%s raw_args=%s" % (tool_name, args))
        use_sudo = False
        if args and args[0] == "--sudo":
            use_sudo = True
            args = args[1:]
        if args and args[0] in tool.get("admin_subcommands", set()):
            use_sudo = True
        Log.debug("winsh sudo=%s args=%s" % (use_sudo, args))

        cmd = [tool["exe"]] + args
        if use_sudo:
            cmd = ["gsudo.exe"] + cmd
        cmd = self.__resolve_cmd(cmd)
        Log.debug("winsh exec cmd: %s" % " ".join(shlex.quote(item) for item in cmd))

        try:
            Log.debug("winsh windows cwd: %s" % self.__windows_cwd())
            ret = subprocess.call(cmd, cwd=self.__windows_cwd())
            Log.debug("winsh exec status: %s" % ret)
            return ret
        except FileNotFoundError as e:
            missing = e.filename or cmd[0]
            Log.error("找不到 Windows 命令: %s" % missing)
            Log.tips("请确认 WSL interop 已启用，并且该命令在 Windows PATH 中。")
            return 127

    def __run_usbipd(self, args):
        return self.__run_windows_tool("usbipd", args)

    def exec(self):
        args = self.__args_list if self.__args_list else self.arg_list[1:]
        Log.debug("winsh exec args: %s" % args)
        if self.should_show_help(args):
            self.help(args[0] if args else None)
            return
        if not args:
            self.help()
            return
        use_sudo = False
        if args and args[0] == "--sudo":
            use_sudo = True
            args = args[1:]
        Log.debug("winsh global sudo=%s args=%s" % (use_sudo, args))
        if not args:
            self.help()
            return
        command = args[0]
        if command not in self.option_dic:
            Log.error("未知 Windows 工具: %s" % shlex.quote(command))
            self.help()
            return
        tool_args = args[1:]
        if use_sudo:
            tool_args = ["--sudo"] + tool_args
        Log.debug("winsh dispatch command=%s tool_args=%s" % (command, tool_args))
        return self.option_dic[command](tool_args)
