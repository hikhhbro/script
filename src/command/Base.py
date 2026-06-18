import os
import sys
import copy
from command.Shell import Shell
from command.Listdirs import CurFile
import importlib
from command.Json import Json

class Arg:
    def __init__(self):
        self.arg_list = copy.copy(sys.argv)
        self.isend = None
        self.cur = ""

        if self.arg_list and self.arg_list[-1] in ["n", "y"]:
            self.isend = self.arg_list[-1] == "y"
            del self.arg_list[-1]

        tool_name = os.getenv("SCRIPT_TOOL_NAME") or ""
        if self.arg_list and (
            self.arg_list[0].endswith(".py")
            or (tool_name and "/" + tool_name in self.arg_list[0])
        ):
            del self.arg_list[0]

        if self.isend is False and self.arg_list:
            self.cur = self.arg_list[-1]
            del self.arg_list[-1]

    def last_cur(self, num):
        if len(self.arg_list) < 2:
            return self.cur
        if self.cur and num < len(self.arg_list):
            return self.arg_list[-(num + 1)]
        return ""


class HelpMixin:
    """中文帮助混入类：所有工具默认继承这一套 --help 行为。"""

    help_flags = {"--help", "-h", "help"}
    help_summary = "终端工具模块"
    help_usage = "{tool_name} {module_name} [选项]"
    help_options = {}
    help_examples = []

    def normalize_args(self, args):
        """把外部传入参数统一成列表，方便各模块复用。"""
        if isinstance(args, list):
            return args
        if args:
            return [args]
        return []

    def should_show_help(self, args=None):
        """判断参数中是否包含公共帮助开关。"""
        args = self.normalize_args(args)
        return any(item in self.help_flags for item in args)

    def module_name(self):
        """把类名转换成命令名，首字母小写即可匹配现有工具。"""
        return self.__class__.__name__.lower()

    def format_usage(self):
        """渲染用法行，模块可通过 help_usage 自定义模板。"""
        return self.help_usage.format(
            tool_name=self.tool_name,
            module_name=self.module_name(),
        )

    def help(self, command=None):
        """打印中文帮助；command 存在时优先打印子命令说明。"""
        print("用法: %s" % self.format_usage())
        if self.help_summary:
            print("说明: %s" % self.help_summary)

        options = getattr(self, "help_options", {}) or {}
        if command and command in options:
            print("\n子命令:")
            print("  %-18s %s" % (command, options[command]))
        elif options:
            print("\n子命令/选项:")
            for name, desc in options.items():
                print("  %-18s %s" % (name, desc))

        examples = getattr(self, "help_examples", []) or []
        if examples:
            print("\n示例:")
            for item in examples:
                print("  %s" % item)


class Base(HelpMixin, Arg):
    def __init__(self, args_list: list = None, config_name="config.json"):
        super().__init__()
        self.args_list = self.normalize_args(args_list)
        self.tool_dir = os.getenv("SCRIPT_TOP_DIR") or os.getcwd()
        self.tool_name = os.getenv("SCRIPT_TOOL_NAME") or "hikrun"
        self.option_dic = {}
        self.data_dir = os.path.join(self.tool_dir, "data", self.__class__.__name__.lower()) + "/"
        self.config = Json(self.data_dir + config_name)

        if not os.path.exists(self.config.path):
            os.makedirs(self.data_dir, exist_ok=True)
            self.config.write({})
        
    def _opt(self):
        return Opt(list(self.option_dic.keys()))

    def exec(self):
        """默认执行入口：先处理公共帮助，再分发到子命令。"""
        args = self.args_list if self.args_list else self.arg_list[1:]
        if self.should_show_help(args):
            self.help(args[0] if args and args[0] in self.option_dic else None)
            return
        if not args or args[0] not in self.option_dic:
            self.help()
            return
        self.option_dic[args[0]](args[1:])


class Myclass:
    def __init__(self):
        sys.path.append(os.getenv("SCRIPT_TOP_DIR") + "/src/utils")
        self.arg = Arg()

    def get_sub_tool(self):
        if not self.arg.arg_list:
            raise ValueError("missing sub tool")
        out = self.arg.arg_list[0]
        model = importlib.import_module(out.capitalize())
        return getattr(model, out.capitalize())

    def get_class(self):
        if len(self.arg.arg_list) == 1 and self.arg.arg_list[0] == os.getenv(
            "SCRIPT_TOOL_NAME"
        ):
            out = "main"
            package = "main"
        else:
            out = ""
        if self.arg.arg_list:
            del self.arg.arg_list[0]

        tool_name = ""
        if self.arg.isend:
            if len(self.arg.arg_list) > 0:
                tool_name = self.arg.arg_list[0]
                out = tool_name.capitalize()
                del self.arg.arg_list[0]
        else:
            if len(self.arg.arg_list) > 0:
                tool_name = self.arg.arg_list[0]
                out = tool_name.capitalize()
                del self.arg.arg_list[0]

        # shell 脚本和子目录路径没有 Python 模块，补全时回退到 main。
        if tool_name:
            from command.CompTemp import CompTemp
            if '/' in tool_name or CompTemp().get(tool_name):
                out = "main"

        model = importlib.import_module(out)
        return getattr(model, out)

    def get_opname(self, last=1):
        if len(self.arg.arg_list) > 0 and last <= len(self.arg.arg_list):
            if self.arg.arg_list[-last] and self.arg.arg_list[-last][0] != "-":
                return self.arg.arg_list[-last]
            return ""
        else:
            return ""


class Opt:
    def __init__(self, opt=None, file_opt=False):
        self.opt = {"long": ["--help"], "short": [], "sub": []}
        self.file_opt = file_opt
        self.retreat = ""
        if opt:
            if isinstance(opt, list):
                for item in opt:
                    self.opt_type(item).append(item)
            else:
                self.opt_type(opt).append(opt)

    def get_long_opt(self):
        return self.opt["long"]

    def get_short_opt(self):
        return self.opt["short"]

    def get_sub_opt(self):
        return self.opt["sub"]

    def set_long_opt(self, opt):
        if isinstance(opt, list):
            self.opt["long"] = self.opt["long"] + opt
        else:
            self.opt["long"].append(opt)

    def set_short_opt(self, opt):
        if isinstance(opt, list):
            self.opt["short"] = self.opt["short"] + opt
        else:
            self.opt["short"].append(opt)

    def set_sub_opt(self, opt):
        if isinstance(opt, list):
            self.opt["sub"] = self.opt["sub"] + opt
        else:
            self.opt["sub"].append(opt)

    def opt_type(self, arg):
        if not arg:
            return self.get_sub_opt()
        if "--" == arg[0:2]:
            opt = self.get_long_opt()
        elif "-" in arg[0]:
            opt = self.get_short_opt()
        else:
            opt = self.get_sub_opt()
        return opt

    def shield_opt(self, scope="all"):
        if self.retreat:
            if scope == "all":
                self.opt_type(self.retreat).clear()
            else:
                self.opt_type(self.retreat).remove(self.retreat)
