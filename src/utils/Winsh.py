import re

import Log
from command.Base import Base
from command.Shell import Shell


class Winsh(Base):
    def __init__(self, args=None):
        super().__init__(args)
        self.meta("从 WSL 调用 Windows 侧命令，并提供常用工具的分层补全。")
        self.win = Shell.win()
        self.windows_tools = {
            "usbipd": {
                "exe": "usbipd.exe",
                "admin_subcommands": {"bind", "unbind"},
            },
        }
        self.command_tree.long('--sudo', '强制使用 gsudo.exe 提权执行后续 Windows 命令', inherit=True)
        usbipd = self.command("usbipd", "管理 Windows USB/IP 设备并连接到 WSL").run(self.__run_usbipd)
        usbipd.command("list", "列出 USB 设备") \
            .long("--usbids", "显示 USB ID") \
            .long("--parsable", "输出机器可解析格式")
        usbipd.command("state", "显示 usbipd 服务状态")
        usbipd.command("bind", "绑定 USB 设备") \
            .long("--busid", "指定设备 busid", values=self.__usbipd_busids) \
            .long("--force", "强制执行") \
            .args("--busid <busid>")
        usbipd.command("unbind", "解绑 USB 设备") \
            .long("--busid", "指定设备 busid", values=self.__usbipd_busids) \
            .long("--force", "强制执行") \
            .args("--busid <busid>")
        usbipd.command("attach", "连接 USB 设备到 WSL") \
            .long("--busid", "指定设备 busid", values=self.__usbipd_busids) \
            .long("--wsl", "连接到默认 WSL") \
            .long("--distribution", "指定 WSL 发行版", values=self.__wsl_distros) \
            .long("--auto-attach", "启用自动连接") \
            .args("--busid <busid> [--wsl]")
        usbipd.command("detach", "断开 USB 设备") \
            .long("--busid", "指定设备 busid", values=self.__usbipd_busids) \
            .args("--busid <busid>")
        Log.debug("winsh args: %s" % self.args)
        Log.debug("winsh tools: %s" % list(self.windows_tools))

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
        busids = [
            match.group(1) for line in out.splitlines()
            if (match := re.match(r"^\s*([0-9]+-[0-9]+)\s+", line))
        ]
        Log.debug("winsh usbipd busids: %s" % busids)
        return busids

    def __wsl_distros(self):
        out = self.__run(["wsl.exe", "-l", "-q"])
        distros = [name for line in out.splitlines() if (name := line.replace("\x00", "").strip())]
        Log.debug("winsh wsl distros: %s" % distros)
        return distros

    def __run_windows_tool(self, tool_name, args):
        tool = self.windows_tools.get(tool_name)
        if not tool:
            Log.error("未知 Windows 工具: %s" % tool_name)
            return 1

        Log.debug("winsh run tool=%s raw_args=%s" % (tool_name, args))
        use_sudo = "--sudo" in args
        args = [item for item in args if item != "--sudo"]
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
        Log.debug("winsh exec args: %s" % self.args)
        return self.dispatch()
