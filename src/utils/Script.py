import os
import Log
from command.Shell import Shell
from command.CompTemp import CompTemp
from command.Base import Base

class Script(Base):
    def __init__(self, args=None):
        super().__init__(args)
        self.meta("管理 hikrun 的 shell 脚本。")
        self.command('readme', '打开 README 并提交更新').run(self.__readme)
        self.command('build', '扫描 shell 目录并刷新脚本补全缓存').run(self.__build)
        self.command('rm', '把脚本移动到回收目录').run(self.__rm).value(lambda ctx: self.files(self.shell_path(), ctx.current)).args("<脚本>")
        self.command('add', '新增脚本并打开编辑器').run(self.__add).value(lambda ctx: self.files(self.shell_path(), ctx.current)).args("<脚本>")
    def __readme(self,text = None):
        Shell.code(os.path.join(self.tool_dir, 'README.md'), wait=True).status()
        Shell.chain(cwd=self.tool_dir).git('add', 'README.md').git('commit', '-m', '更新READEME').status()
    
    def __build(self,text = None):
        dir_opt = self.files(self.shell_path(), is_=["exe_file"])
        CompTemp().set(dir_opt)
            
        # print(dir_opt)
    def __rm(self,text = None):
        if not text:
            return
        target = text[-1]
        src = self.shell_path(target)
        dst_dir = self.shell_path('.resycle', os.path.dirname(target))
        dst = self.shell_path('.resycle', target)

        if not os.path.exists(src):
            Log.error("文件不存在: %s" % target)
            return

        if Shell.chain().mkdir(dst_dir).cmd('mv', src, dst).status() == 0:
            CompTemp().delete([target])
        else:
            Log.error("删除失败: %s" % target)

    def __add(self,text = None):
        target_name = text[-1]
        target = self.shell_path(target_name)
        Shell.chain().cmd('touch', target).cmd('code', target).cmd('chmod', '777', target).status()
        CompTemp().set([target_name])
