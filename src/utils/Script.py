import os
import Log
from command.Shell import Shell
from command.CompTemp import CompTemp
from command.Listdirs import CurFile
from command.Base import Base
from command.Base import Opt

class Script(Base):
    help_summary = "管理 hikrun 的 shell 脚本。"
    help_usage = "{tool_name} script <子命令> [参数]"
    help_options = {
        "readme": "打开 README 并提交更新",
        "build": "扫描 shell 目录并刷新脚本补全缓存",
        "rm": "把脚本移动到回收目录",
        "add": "新增脚本并打开编辑器",
    }
    help_examples = [
        "hikrun script add demo",
        "hikrun script rm demo",
        "hikrun script build",
    ]

    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.set_commands({
            'readme' : self.__readme,
            'build' : self.__build,
            'rm' : self.__rm,
            'add' : self.__add,
        })
        self.shell_dir = self.tool_path('shell')
        self.company_shell_dir = self.tool_path('shell', 'company')
    def __readme(self,text = None):
        Shell.code(os.path.join(self.tool_dir, 'README.md'), wait=True).status()
        Shell.chain(cwd=self.tool_dir).git('add', 'README.md').git('commit', '-m', '更新READEME').status()
    
    def __build(self,text = None):
        dir_opt = self.files(self.shell_dir, is_=["exe_file"])
        CompTemp().set(dir_opt)
            
        # print(dir_opt)
    def __rm(self,text = None):
        if not text:
            return
        target = text[-1]
        src = '%s/%s' % (self.shell_dir, target)
        dst_dir = '%s/.resycle/%s' % (self.shell_dir, os.path.dirname(target))
        dst = '%s/.resycle/%s' % (self.shell_dir, target)

        if not os.path.exists(src):
            Log.error("文件不存在: %s" % target)
            return

        if Shell.chain().mkdir(dst_dir).cmd('mv', src, dst).status() == 0:
            CompTemp().delete([target])
        else:
            Log.error("删除失败: %s" % target)
    def __add(self,text = None):
        target = os.path.join(self.shell_dir, text[-1])
        Shell.chain().cmd('touch', target).cmd('code', target).cmd('chmod', '777', target).status()
        CompTemp().set([text[-1]])
        
    def add_opt(self):
        return self.file_opt(self.shell_dir, self.cur)

    def rm_opt(self):
        return self.add_opt()
