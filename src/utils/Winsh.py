import re
import shlex

import Log
from command.Base import Base, Opt
from command.Shell import Shell


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
        self.win = Shell.win()
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

    def __run(self, cmd):
        try:
            out = self.win.stdout(*cmd)
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
        Log.debug("winsh exec cmd: %s" % Shell.format(cmd))

        try:
            ret = self.win.status(*cmd, sudo=use_sudo)
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
