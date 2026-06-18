# -*- coding: utf-8 -*-

import os
import shlex
import Log
from command.Shell import Shell
from command.Base import Base, Opt
from command.Listdirs import CurFile


class Note(Base):
    help_summary = "在终端中创建、编辑、初始化和同步 Markdown 笔记。"
    help_usage = "{tool_name} note <子命令> [参数]"
    help_options = {
        "code": "创建或打开笔记文件/目录",
        "sync": "提交并推送笔记仓库",
        "init": "克隆并初始化笔记仓库",
        "--help": "显示当前帮助",
    }
    help_examples = [
        "hikrun note code 公司/test",
        "hikrun note sync github 更新笔记",
        "hikrun note init git@github.com:user/notes.git /ws/note",
    ]

    def __init__(self, args_list=None):
        super().__init__()
        if isinstance(args_list, list):
            self.__args_list = args_list
        elif args_list:
            self.__args_list = [args_list]
        else:
            self.__args_list = []
        self.option_dic = {
            'code': self._code,
            'sync': self._sync,
            'init': self._init,
        }
        self._load_note_root()
        Log.debug('Note init: args=%s note_root=%s' % (self.__args_list, self.note_root))

    def _load_note_root(self):
        """从配置读取 note_root，默认使用 /ws/note。"""
        try:
            cfg = self.config.read()
            if 'note_root' in cfg:
                self.note_root = cfg['note_root']
                Log.debug('note_root loaded from config: %s' % self.note_root)
            else:
                self.note_root = '/ws/note'
                self.config.write({'note_root': '/ws/note'})
                Log.debug('note_root defaulted to: %s' % self.note_root)
        except Exception:
            self.note_root = '/ws/note'
            self.config.write({'note_root': '/ws/note'})
            Log.debug('note_root config read failed, defaulted to: %s' % self.note_root)

    # ---- Subcommand handlers ----

    def _code(self, args):
        """在笔记根目录创建或打开文件/目录。

        路径直接写在参数里：
          hikrun note code 公司/test     -> 创建 公司/test.md（自动补 .md）
          hikrun note code 公司/test.md  -> 创建 公司/test.md（显式扩展名）
          hikrun note code 公司/         -> 创建目录 公司/
        """
        Log.debug('_code args=%s' % args)

        if not args:
            Log.tips("Usage: hikrun note code <path>[/<filename>]")
            return

        target = ' '.join(args)
        Log.debug('_code target=%s' % target)

        # 目录创建：路径以 / 结尾
        if target.endswith('/'):
            full_path = os.path.join(self.note_root, target)
            Log.debug('creating directory: %s' % full_path)
            Shell('mkdir -p ' + shlex.quote(full_path)).exec_system()
            Log.tips('Created directory: %s' % full_path)
            return

        # 文件创建：文件名没有扩展名时自动补 .md
        if '/' in target:
            basename = target.split('/')[-1]
        else:
            basename = target
        if '.' not in basename:
            target = target + '.md'
            Log.debug('auto .md: %s' % target)

        full_path = os.path.join(self.note_root, target)
        Log.debug('full_path=%s' % full_path)

        dir_part = os.path.dirname(full_path)
        if not os.path.exists(dir_part):
            Log.debug('mkdir -p %s' % dir_part)
            Shell('mkdir -p ' + shlex.quote(dir_part)).exe()

        Shell('code ' + shlex.quote(full_path)).exec_system()

    def _sync(self, args):
        """在笔记根目录执行 git add、commit、push。

        hikrun note sync                -> 使用默认远端，提交信息为 sync
        hikrun note sync hik            -> 本次推送到 hik
        hikrun note sync github msg     -> 推送到 github，提交信息为 msg
        hikrun note sync --default hik  -> 修改默认远端为 hik

        默认远端只在首次同步或显式使用 --default/-d 时保存。
        """
        Log.debug('_sync args=%s' % args)

        cfg = self.config.read()
        default_remote = cfg.get('default_remote', 'hik')
        Log.debug('_sync cfg=%s default_remote=%s' % (cfg, default_remote))

        # 获取已配置的远端列表
        try:
            known = Shell('git -C %s remote' % shlex.quote(self.note_root)).exe().strip().split('\n')
            known = [r for r in known if r]  # 过滤空行
        except Exception:
            known = []
        Log.debug('_sync known remotes=%s' % known)

        # 解析显式 --default/-d 参数
        set_default = None
        i = 0
        while i < len(args):
            if args[i] in ('-d', '--default'):
                if i + 1 < len(args):
                    set_default = args[i + 1]
                    del args[i:i + 2]
                else:
                    Log.error("-d/--default requires a remote name")
                    return
            else:
                i += 1

        if set_default:
            Log.debug('setting default remote to: %s' % set_default)
            cfg['default_remote'] = set_default
            self.config.write(cfg)
            default_remote = set_default
            Log.tips('Default remote set to: %s' % set_default)

        # 区分远端名和提交信息
        if args and args[0] in known:
            remote = args[0]
            message = ' '.join(args[1:]) if len(args) > 1 else 'sync'
        else:
            remote = default_remote
            message = ' '.join(args) if args else 'sync'

        Log.debug('_sync remote=%s message=%s' % (remote, message))

        # 仅首次同步保存默认远端，本次临时远端不覆盖默认值
        if 'default_remote' not in cfg:
            cfg['default_remote'] = remote
            self.config.write(cfg)
            Log.debug('first sync, saving default_remote=%s' % remote)
            Log.tips('Default remote set to: %s' % remote)

        Shell(
            'cd %s && git add . && git commit -m %s && git push %s'
            % (shlex.quote(self.note_root), shlex.quote(message), shlex.quote(remote))
        ).exec_system()

    def _init(self, args):
        """克隆远端笔记仓库，并设置为笔记根目录。

        用法：hikrun note init <remote_url> <target_path>

        note_root 配置保存在本地 data/note/config.json，不随笔记仓库上传。
        """
        Log.debug('_init args=%s' % args)

        if len(args) < 2:
            Log.tips("Usage: hikrun note init <remote_url> <path>")
            Log.tips("Example: hikrun note init git@github.com:user/notes.git /ws/note")
            return

        remote_url = args[0]
        target_path = args[1]
        Log.debug('_init remote_url=%s target_path=%s' % (remote_url, target_path))

        if os.path.exists(target_path):
            if os.path.exists(os.path.join(target_path, '.git')):
                Log.tips('Directory exists and is a git repo, pulling...')
                Shell('cd %s && git pull' % shlex.quote(target_path)).exec_system()
            else:
                Log.error('path exists but is not a git repository')
                return
        else:
            parent_dir = os.path.dirname(target_path)
            if not os.path.exists(parent_dir):
                Log.debug('mkdir -p %s' % parent_dir)
                Shell('mkdir -p ' + shlex.quote(parent_dir)).exe()
            Log.tips('Cloning %s -> %s ...' % (remote_url, target_path))
            Shell('git clone %s %s' % (shlex.quote(remote_url), shlex.quote(target_path))).exec_system()

        self.note_root = target_path
        self.config.write({'note_root': target_path})
        Log.debug('note_root updated to: %s' % target_path)
        Log.tips('Note root set to: %s' % target_path)

    # ---- 补全方法 ----

    def _opt(self):
        """顶层补全：只返回 code、sync、init 等子命令。"""
        return Opt(list(self.option_dic.keys()))

    def code_opt(self):
        """code 后的路径补全：返回目录和文件用于导航。"""
        return Opt(CurFile(self.note_root).get_file_opt(self.cur))

    def sync_opt(self):
        """sync 补全：已知远端和 --default/-d。"""
        try:
            remotes = Shell('git -C %s remote' % shlex.quote(self.note_root)).exe().strip().split('\n')
            remotes = [r for r in remotes if r]
        except Exception:
            remotes = []
        return Opt(remotes + ['--default', '-d'])

    def init_opt(self):
        """init 不做固定补全，URL 和路径自由输入。"""
        return Opt([])

    def __getattr__(self, name):
        """动态路径补全：处理类似 公司/_opt 的查询。

        complete.py 在路径参数后遇到空格时会查找对应的 _opt 方法，
        这里返回一个 lambda 来列出该目录内容，避免补全回退逻辑清空选项。
        """
        if name.endswith('_opt') and '/' in name[:-4]:
            path = name[:-4]  # 去掉 _opt 后缀
            return lambda: Opt(CurFile(self.note_root).get_file_opt(path))
        raise AttributeError(name)

    # ---- 命令分发 ----

    def exec(self):
        """分发 note 子命令，优先处理公共帮助。"""
        Log.debug('exec args=%s' % self.__args_list)
        if self.should_show_help(self.__args_list):
            command = self.__args_list[0] if self.__args_list and self.__args_list[0] in self.option_dic else None
            self.help(command)
            return

        subcommand = None
        subcommand_idx = -1
        for i, arg in enumerate(self.__args_list):
            if arg in self.option_dic:
                subcommand = arg
                subcommand_idx = i
                break

        if subcommand is None:
            self.help()
            return

        Log.debug('exec dispatching to %s, sub_args=%s' % (subcommand, self.__args_list[subcommand_idx + 1:]))
        sub_args = self.__args_list[subcommand_idx + 1:]
        self.option_dic[subcommand](sub_args)
