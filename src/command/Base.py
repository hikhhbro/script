import os
import sys
import copy
import inspect
from command.Shell import Shell
from command.Listdirs import CurFile
import importlib
from command.Json import Json


class CompletionContext:
    """补全上下文：把 bash 传入的光标状态解析成可复用判断接口。

    约定:
      - words 是当前模块后的已确认参数，不包含正在输入的 current。
      - current 是正在输入的半截 token；光标在空格后时为空字符串。
      - isend 表示光标前是空格。
    """

    def __init__(self, argv=None, module_name=None, tool_name=None):
        argv = list(argv if argv is not None else sys.argv)
        self.raw_argv = list(argv)
        self.tool_name = tool_name or os.getenv("SCRIPT_TOOL_NAME") or "hikrun"
        self.module_name = module_name
        self.isend = False
        self.current = ""

        if argv and argv[-1] in ["n", "y"]:
            self.isend = argv[-1] == "y"
            argv = argv[:-1]

        if argv and argv[0].endswith(".py"):
            argv = argv[1:]
        if argv and (argv[0] == self.tool_name or argv[0].endswith("/" + self.tool_name)):
            argv = argv[1:]
        if self.module_name and argv and argv[0] == self.module_name:
            argv = argv[1:]

        if not self.isend and argv:
            self.current = argv[-1]
            argv = argv[:-1]

        self.words = argv

    def prev(self, offset=1, default=None):
        if len(self.words) >= offset:
            return self.words[-offset]
        return default

    def current_is_option(self):
        return self.current.startswith("-")

    def option_name_from_current(self):
        if self.current.startswith("--") and "=" in self.current:
            return self.current.split("=", 1)[0]
        return self.current if self.current.startswith("-") else None

    def value_option(self, option_values):
        """返回当前正在补值的 option 名。

        option_values 是 {"--name": provider_or_values}。支持:
          --name <value>
          --name=<value>
        """
        if not option_values:
            return None
        current_name = self.option_name_from_current()
        if current_name in option_values and "=" in self.current:
            return current_name
        prev = self.prev()
        if prev in option_values:
            return prev
        return None

    def items(self, values=None, file_opt=False):
        return Opt(values or [], file_opt)

    def options(self, values=None):
        opt = Opt([])
        for item in values or []:
            opt.add(item)
        return opt

    def values_for(self, option_values, option_name=None):
        option_name = option_name or self.value_option(option_values)
        provider = option_values.get(option_name) if option_name else None
        values = self.call_provider(provider)
        if self.current.startswith("--") and "=" in self.current and option_name:
            opt = Opt([])
            opt.set_long_opt([option_name + "=" + value for value in values])
            return opt
        return Opt(values)

    def call_provider(self, provider):
        if not callable(provider):
            return provider or []
        try:
            if len(inspect.signature(provider).parameters) >= 1:
                return provider(self) or []
        except Exception:
            pass
        return provider() or []

    def node_values(self, node):
        values = node.get("_values")
        if values is None:
            return None
        values = self.call_provider(values)
        return Opt(values or [], node.get("_file_opt", False))

    def complete_tree(self, tree, root_options=None):
        """按声明式命令树补全。

        tree 示例:
        {
          "usbipd": {
            "_commands": {
              "bind": {
                "_options": {"--busid": busid_provider, "--force": None}
              }
            }
          }
        }
        """
        node = {"_commands": tree, "_options": root_options or {}}
        index = 0
        while index < len(self.words):
            commands = node.get("_commands", {})
            word = self.words[index]
            if word.startswith("-"):
                index += 1
                continue
            if word in commands:
                node = commands[word] or {}
                index += 1
                continue
            break

        option_values = {
            key: value for key, value in (node.get("_options", {}) or {}).items()
            if value is not None
        }
        value_option = self.value_option(option_values)
        if value_option:
            return self.values_for(option_values, value_option)

        if self.current_is_option():
            return self.options(list((node.get("_options", {}) or {}).keys()))

        values_opt = self.node_values(node)
        if values_opt is not None:
            return values_opt

        return self.items(list((node.get("_commands", {}) or {}).keys()))

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
        parts = [self.tool_name]
        if self.module_name() != "main":
            parts.append(self.module_name())
        parts.append("[参数]")
        return " ".join(parts)

    def help(self, command=None):
        """打印中文帮助；command 存在时优先打印子命令说明。"""
        print("用法: %s" % self.format_usage())
        if self.help_summary:
            print("说明: %s" % self.help_summary)

        print("\n子命令/选项:")
        print("  %-18s %s" % ("--help", "显示当前帮助"))


class CommandOption:
    def __init__(self, name, desc="", values=None, inherit=False, file_opt=False):
        self.name = name
        self.desc = desc
        self.values = values
        self.inherit = inherit
        self.file_opt = file_opt

    def value(self, values, file_opt=False):
        self.values = values
        self.file_opt = file_opt
        return self


class CommandNode:
    def __init__(self, name="", desc="", handler=None, parent=None):
        self.name = name
        self.desc = desc
        self.handler = handler
        self.parent = parent
        self.children = {}
        self.options = {}
        self.value_provider = None
        self.file_opt = False
        self.args_hint = ""

    def command(self, name, desc="", handler=None):
        if name in self.children:
            node = self.children[name]
            if desc:
                node.desc = desc
            if handler:
                node.handler = handler
            return node
        node = CommandNode(name, desc, handler, self)
        self.children[name] = node
        return node

    def run(self, handler):
        self.handler = handler
        return self

    def option(self, name, desc="", values=None, inherit=False, file_opt=False):
        opt = CommandOption(name, desc, values, inherit, file_opt)
        self.options[name] = opt
        return self

    def long(self, name, desc="", values=None, inherit=False, file_opt=False):
        if not name.startswith("--"):
            name = "--" + name
        return self.option(name, desc, values, inherit, file_opt)

    def short(self, name, desc="", values=None, inherit=False, file_opt=False):
        if not name.startswith("-"):
            name = "-" + name
        return self.option(name, desc, values, inherit, file_opt)

    def value(self, values, file_opt=False):
        self.value_provider = values
        self.file_opt = file_opt
        return self

    def args(self, hint):
        self.args_hint = hint
        return self

    def has_items(self):
        return bool(self.children or self.options or self.handler or self.value_provider is not None)

    def path(self):
        out = []
        node = self
        while node and node.name:
            out.append(node.name)
            node = node.parent
        return list(reversed(out))

    def usage_parts(self):
        parts = self.path()
        if self.args_hint:
            parts.append(self.args_hint)
        return parts

    def first_example_path(self):
        if self.children:
            for child in self.children.values():
                path = child.first_example_path()
                if path:
                    return path
        if self.name and (self.args_hint or self.handler or self.value_provider is not None):
            return self.usage_parts()
        return []

    def inherited_options(self):
        out = {}
        lineage = []
        node = self.parent
        while node:
            lineage.append(node)
            node = node.parent
        for item in reversed(lineage):
            for name, opt in item.options.items():
                if opt.inherit:
                    out[name] = opt
        return out

    def active_options(self):
        out = self.inherited_options()
        out.update(self.options)
        return out

    def option_name(self, word):
        if word.startswith("--") and "=" in word:
            return word.split("=", 1)[0]
        return word if word.startswith("-") else None

    def parse(self, args, search_anywhere=False):
        node = self
        handler_node = self if self.handler else None
        handler_index = -1
        prefix_args = []
        index = 0
        while index < len(args):
            word = args[index]
            if word in node.children:
                node = node.children[word]
                if node.handler:
                    handler_node = node
                    handler_index = index
                index += 1
                continue

            opt_name = self.option_name(word)
            opt = node.active_options().get(opt_name)
            if opt:
                if handler_index < 0:
                    prefix_args.append(word)
                if opt.values is not None and "=" not in word and index + 1 < len(args):
                    if handler_index < 0:
                        prefix_args.append(args[index + 1])
                    index += 2
                else:
                    index += 1
                continue

            if search_anywhere:
                index += 1
                continue
            break
        return node, handler_node, handler_index, prefix_args

    def __call_provider(self, provider, ctx=None):
        if not callable(provider):
            return provider or []
        if ctx is not None:
            try:
                if len(inspect.signature(provider).parameters) >= 1:
                    return provider(ctx) or []
            except Exception:
                pass
        return provider() or []

    def complete(self, ctx):
        node, _, _, _ = self.parse(ctx.words)
        options = node.active_options()
        value_opt_name = ctx.value_option({
            name: opt.values for name, opt in options.items()
            if opt.values is not None
        })
        if value_opt_name:
            opt = options[value_opt_name]
            values = self.__call_provider(opt.values, ctx)
            if ctx.current.startswith("--") and "=" in ctx.current:
                out = Opt.empty()
                out.set_long_opt([value_opt_name + "=" + value for value in values])
                return out
            return Opt(values or [], opt.file_opt)

        if ctx.current_is_option():
            return ctx.options(list(options.keys()))

        values = list(node.children.keys())
        if node.value_provider is not None:
            values += list(self.__call_provider(node.value_provider, ctx))
        return Opt(values, node.file_opt)

    def help_items(self):
        out = {}
        for name, child in self.children.items():
            out[name] = child.desc
        for name, opt in self.active_options().items():
            out[name] = opt.desc
        return out


class Base(HelpMixin, Arg):
    """所有 Python 工具的公共基类。

    新增工具时优先复用:
      1. __init__ 里 super().__init__(args_list)
      2. self.command("子命令", "说明").run(self.xxx)
      3. 不需要特殊逻辑时直接继承 exec()
    """

    def __init__(self, args_list: list = None, config_name="config.json"):
        super().__init__()
        self.args_list = self.normalize_args(args_list)
        # args 是推荐的新入口；保留 args_list 兼容历史代码。
        self.args = self.args_list
        self.name = self.__class__.__name__.lower()
        self.tool_dir = os.getenv("SCRIPT_TOP_DIR") or os.getcwd()
        self.tool_name = os.getenv("SCRIPT_TOOL_NAME") or "hikrun"
        self.option_dic = {}
        self.command_tree = CommandNode()
        self.help_summary = "终端工具模块"
        self.usage_hint = ""
        self.data_dir = os.path.join(self.tool_dir, "data", self.name) + "/"
        self.config = Json(self.data_dir + config_name)

        self.config.ensure({})
        
    def complete(self, ctx):
        if self.command_tree.has_items():
            return self.command_tree.complete(ctx)
        return Opt.empty()

    def command(self, name, desc="", handler=None):
        node = self.command_tree.command(name, desc, handler)
        if handler:
            self.option_dic[name] = handler
        return node

    def meta(self, summary=None, args=None):
        if summary is not None:
            self.help_summary = summary
        if args is not None:
            self.usage_hint = args
        return self

    def format_usage(self, node=None):
        parts = [self.tool_name]
        if self.module_name() != "main":
            parts.append(self.module_name())
        if node is not None and node is not self.command_tree:
            parts += node.usage_parts()
        elif self.usage_hint:
            parts.append(self.usage_hint)
        elif self.command_tree.children:
            parts.append("<子命令>")
        else:
            parts.append("[参数]")
        return " ".join(parts)

    def examples(self, node=None):
        target = node or self.command_tree
        parts = target.first_example_path()
        out = [self.tool_name]
        if self.module_name() != "main":
            out.append(self.module_name())
        if not parts:
            if target is self.command_tree and self.usage_hint:
                return [" ".join(out + [self.usage_hint])]
            if target is not self.command_tree:
                return [" ".join(out + target.usage_parts())]
            return []
        out += parts
        return [" ".join(out)]

    def default(self, handler):
        self.command_tree.run(handler)
        return self.command_tree

    def data_path(self, *parts):
        return os.path.join(self.data_dir, *parts)

    def tool_path(self, *parts):
        return os.path.join(self.tool_dir, *parts)

    def ensure_dir(self, *parts):
        path = os.path.join(*parts) if len(parts) > 1 else parts[0]
        os.makedirs(path, exist_ok=True)
        return path

    def config_read(self, default=None, merge=False):
        return self.config.read(default or {}, merge=merge)

    def config_write(self, data):
        self.config.write(data)
        return data

    def config_update(self, data=None, **kwargs):
        return self.config.update(data, **kwargs)

    def config_get(self, key, default=None):
        return self.config.get(key, default)

    def config_set(self, key, value):
        return self.config.set(key, value)

    def files(self, root=None, postfix='', is_=None, exclude=None):
        return CurFile(root).get_file_opt(postfix, is_, exclude)

    def file_opt(self, root=None, postfix='', is_=None, exclude=None):
        return Opt(self.files(root, postfix, is_, exclude))

    def completion(self, values=None, file_opt=False):
        return Opt(values or [], file_opt)

    def empty_opt(self):
        return Opt.empty()

    def command_names(self, include_empty=False):
        """返回可补全的子命令名；默认过滤空命令。"""
        if self.command_tree.children:
            return list(self.command_tree.children.keys())
        return [
            name for name in self.option_dic.keys()
            if include_empty or name
        ]

    def find_command(self, args=None):
        """在参数中查找第一个已注册子命令。

        默认只需第一个参数是子命令；Note 这类允许路径前缀的工具
        可以用它复用同一套查找逻辑。
        """
        args = self.normalize_args(self.args if args is None else args)
        if self.command_tree.has_items():
            node, _, index, _ = self.command_tree.parse(args)
            if index >= 0:
                return node.name, index
            return None, -1
        for index, item in enumerate(args):
            if item in self.option_dic:
                return item, index
        return None, -1

    def dispatch(self, args=None, default=None, search_anywhere=False, show_help=True):
        """公共命令分发入口。

        default 传入函数时，未知子命令会交给 default(args) 处理；
        search_anywhere=True 时，会在整个参数列表里寻找子命令。
        """
        args = self.normalize_args(self.args if args is None else args)
        if self.should_show_help(args):
            if self.command_tree.has_items():
                node, _, _, _ = self.command_tree.parse(args, search_anywhere=search_anywhere)
                self.help(node.path())
            else:
                command, _ = self.find_command(args)
                self.help(command)
            return None

        if self.command_tree.has_items():
            _, handler_node, handler_index, prefix_args = self.command_tree.parse(args, search_anywhere=search_anywhere)
            if handler_node is not None:
                return handler_node.handler(prefix_args + args[handler_index + 1:])
            if default is not None:
                return default(args)
            if show_help:
                self.help()
            return None

        command = None
        index = -1
        if search_anywhere:
            command, index = self.find_command(args)
        elif args and args[0] in self.option_dic:
            command, index = args[0], 0

        if command is not None:
            return self.option_dic[command](args[index + 1:])

        if default is not None:
            return default(args)

        if show_help:
            self.help()
        return None

    def exec(self):
        """默认执行入口：先处理公共帮助，再分发到子命令。"""
        args = self.args if self.args else self.arg_list[1:]
        return self.dispatch(args)

    def help(self, command=None):
        if not self.command_tree.has_items():
            return super().help(command)

        node = self.command_tree
        if command:
            parts = command if isinstance(command, list) else self.normalize_args(command)
            for part in parts:
                if part in node.children:
                    node = node.children[part]

        print("用法: %s" % self.format_usage(node))
        if self.help_summary:
            print("说明: %s" % self.help_summary)

        if node is not self.command_tree and node.desc:
            print("\n子命令:")
            print("  %-18s %s" % (node.name, node.desc))

        options = node.help_items()
        if "--help" not in options:
            options["--help"] = "显示当前帮助"
        if options:
            title = "子命令/选项:" if node is self.command_tree else "子命令/选项:"
            print("\n%s" % title)
            for name, desc in options.items():
                print("  %-18s %s" % (name, desc))
        else:
            print("\n子命令/选项:")
            print("  %-18s %s" % ("--help", "显示当前帮助"))

        examples = self.examples(node)
        if examples:
            print("\n示例:")
            for item in examples:
                print("  %s" % item)


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

        if not out:
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
        self.display_root = None
        if opt:
            # 自动继承数据源的 display_root（如 CurFile 返回的 FileList）
            if hasattr(opt, 'display_root'):
                self.display_root = opt.display_root
            if isinstance(opt, list):
                for item in opt:
                    self.add(item)
            else:
                self.add(opt)

    @classmethod
    def empty(cls):
        return cls([])

    @classmethod
    def files(cls, opt=None):
        return cls(opt or [], True)

    def extend(self, values):
        for item in values or []:
            self.add(item)
        return self

    def long(self, values):
        self.set_long_opt(values)
        return self

    def short(self, values):
        self.set_short_opt(values)
        return self

    def sub(self, values):
        self.set_sub_opt(values)
        return self

    def add(self, opt):
        """按选项类型添加补全项，并避免空项和重复项。"""
        if not opt:
            return
        target = self.opt_type(opt)
        if opt not in target:
            target.append(opt)

    def __add_to(self, key, values):
        if isinstance(values, list):
            for item in values:
                self.__add_to(key, item)
            return
        if values and values not in self.opt[key]:
            self.opt[key].append(values)

    def get_long_opt(self):
        return self.opt["long"]

    def get_short_opt(self):
        return self.opt["short"]

    def get_sub_opt(self):
        return self.opt["sub"]

    def set_long_opt(self, opt):
        self.__add_to("long", opt)

    def set_short_opt(self, opt):
        self.__add_to("short", opt)

    def set_sub_opt(self, opt):
        self.__add_to("sub", opt)

    def opt_type(self, arg):
        if not arg:
            return self.get_sub_opt()
        if arg == "-":
            return self.get_short_opt() + self.get_long_opt()
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
