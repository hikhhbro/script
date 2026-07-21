# -*- coding: utf-8 -*-

import os
import re
import Log
from command.Shell import Shell
from command.Base import Base


class Note(Base):
    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.meta("在终端中创建、编辑、初始化和同步 Markdown 笔记。")
        self.__args_list = self.args
        self.command('code', '创建或打开笔记文件/目录').run(self._code).value(self.__note_files).args("<路径>")
        self.command('sync', '提交并推送笔记仓库').run(self._sync) \
            .value(self.__sync_remotes) \
            .long('--default', '修改默认远端', self.__sync_remotes) \
            .short('-d', '修改默认远端', self.__sync_remotes) \
            .args("[远端] [提交信息]")
        self.command('init', '克隆并初始化笔记仓库').run(self._init).args("<remote_url> <path>")
        self._load_note_root()
        Log.debug('Note init: args=%s note_root=%s' % (self.__args_list, self.note_root))

    def __note_files(self, ctx):
        prefix = ctx.current
        if not prefix and ctx.prev() and ctx.prev() not in self.option_dic:
            prefix = ctx.prev()
        return self.files(self.note_root, prefix)

    def _load_note_root(self):
        """从配置读取 note_root，默认使用 /ws/note。"""
        self.note_root = self.config_get('note_root', '/ws/note')
        if self.config_get('note_root') is None:
            self.config_set('note_root', self.note_root)
            Log.debug('note_root defaulted to: %s' % self.note_root)
        else:
            Log.debug('note_root loaded from config: %s' % self.note_root)

    # ---- Subcommand handlers ----

    @staticmethod
    def _next_number(parent_dir, prefix):
        """返回 parent_dir 下可用的下一个序号（两位数）。
        prefix: 'd' 目录, 'f' 文件。
        """
        max_num = 0
        if os.path.isdir(parent_dir):
            try:
                pat = re.compile(r'^' + prefix + r'(\d+)-')
                for item in os.listdir(parent_dir):
                    m = pat.match(item)
                    if m:
                        max_num = max(max_num, int(m.group(1)))
            except OSError:
                pass
        return max_num + 1

    def _code(self, args):
        """在笔记根目录创建或打开文件/目录，自动添加 dNN-/fNN- 序号前缀。
        d=目录(directory), f=文件(file)。

        路径直接写在参数里：
          hikrun note code 公司/test.md      -> 创建 公司/f02-test.md（自动补序号）
          hikrun note code 公司/f03-test.md  -> 已有 fNN- 前缀，直接打开
          hikrun note code 公司/             -> 创建目录 公司/d02-新目录/
          hikrun note code newdir/           -> 创建顶层目录 d15-newdir/
          hikrun note code d03-工具-软件/f01-xxx.md  -> 已有前后缀，直接打开
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
            full_path_norm = os.path.normpath(full_path)
            parent_dir = os.path.dirname(full_path_norm)
            basename = os.path.basename(full_path_norm)
            # 手动指定了 dNN- 或旧格式 NN- 则不再自动补
            if not re.match(r'^d\d+-|^\d+-', basename):
                num = self._next_number(parent_dir, 'd')
                basename = 'd%02d-%s' % (num, basename)
                full_path = os.path.join(parent_dir, basename) + '/'
            elif re.match(r'^\d+-', basename):
                # 旧格式 NN- → 新格式 dNN-
                num = int(re.match(r'^(\d+)-', basename).group(1))
                rest = re.sub(r'^\d+-', '', basename)
                basename = 'd%02d-%s' % (num, rest)
                full_path = os.path.join(parent_dir, basename) + '/'
            Log.debug('creating directory: %s' % full_path)
            Shell.mkdir(full_path).status()
            Log.tips('Created directory: %s' % full_path)
            return

        # 文件创建：文件名没有扩展名时自动补 .md
        if '/' in target:
            dirname, basename = target.rsplit('/', 1)
        else:
            dirname, basename = '', target
        if '.' not in basename:
            basename = basename + '.md'
            Log.debug('auto .md: %s' % basename)

        # 自动补文件序号（fNN-）或兼容旧格式（NN-）
        name, ext = os.path.splitext(basename)
        parent_dir = os.path.join(self.note_root, dirname) if dirname else self.note_root
        if not re.match(r'^f\d+-', name):
            if re.match(r'^\d+-', name):
                # 旧格式 NN- → 新格式 fNN-
                num = int(re.match(r'^(\d+)-', name).group(1))
                rest = re.sub(r'^\d+-', '', name)
                basename = 'f%02d-%s%s' % (num, rest, ext)
            else:
                # 无序号 → 自动分配
                num = self._next_number(parent_dir, 'f')
                basename = 'f%02d-%s%s' % (num, name, ext)
            Log.debug('auto num: %s' % basename)

        target = os.path.join(dirname, basename) if dirname else basename
        full_path = os.path.join(self.note_root, target)
        Log.debug('full_path=%s' % full_path)

        dir_part = os.path.dirname(full_path)
        if not os.path.exists(dir_part):
            Log.debug('mkdir -p %s' % dir_part)
            Shell.mkdir(dir_part).status()

        Shell.code(full_path).status()

    def _sync(self, args):
        """在笔记根目录执行 git add、commit、push。

        hikrun note sync                -> 使用默认远端，提交信息为 sync
        hikrun note sync hik            -> 本次推送到 hik
        hikrun note sync github msg     -> 推送到 github，提交信息为 msg
        hikrun note sync --default hik  -> 修改默认远端为 hik

        默认远端只在首次同步或显式使用 --default/-d 时保存。
        """
        Log.debug('_sync args=%s' % args)

        cfg = self.config_read()
        default_remote = cfg.get('default_remote', 'hik')
        Log.debug('_sync cfg=%s default_remote=%s' % (cfg, default_remote))

        # 获取已配置的远端列表
        try:
            known = Shell.git(self.note_root, 'remote').stdout().strip().split('\n')
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
            self.config_write(cfg)
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
            self.config_write(cfg)
            Log.debug('first sync, saving default_remote=%s' % remote)
            Log.tips('Default remote set to: %s' % remote)

        Shell.chain(cwd=self.note_root) \
            .git('add', '.') \
            .git('commit', '-m', message) \
            .git('push', remote) \
            .status()

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
                Shell.git(target_path, 'pull').status()
            else:
                Log.error('path exists but is not a git repository')
                return
        else:
            parent_dir = os.path.dirname(target_path)
            if not os.path.exists(parent_dir):
                Log.debug('mkdir -p %s' % parent_dir)
                Shell.mkdir(parent_dir).status()
            Log.tips('Cloning %s -> %s ...' % (remote_url, target_path))
            Shell.cmd('git', 'clone', remote_url, target_path).status()

        self.note_root = target_path
        self.config_write({'note_root': target_path})
        Log.debug('note_root updated to: %s' % target_path)
        Log.tips('Note root set to: %s' % target_path)

    def __sync_remotes(self):
        try:
            remotes = Shell.git(self.note_root, 'remote').stdout().strip().split('\n')
            return [r for r in remotes if r]
        except Exception:
            return []

    # ---- 命令分发 ----

    def exec(self):
        """分发 note 子命令，优先处理公共帮助。"""
        Log.debug('exec args=%s' % self.__args_list)
        return self.dispatch(self.__args_list, search_anywhere=True)
