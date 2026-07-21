import os
from command.Base import Base
class Cd(Base):
    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.meta("把 cd 命令写回当前终端输入缓冲区，实现父 shell 跳转。", args="<目录>")
        self.__args_list = self.args
        self.add_dic = { }
        self.command_tree.value(self.__dir_values, file_opt=True)

    def __dir_values(self, ctx):
        prefix = self.__args_list[-1] if self.__args_list else ctx.current
        return self.files(prefix)

    def __quote_against_shell_expansion(self,s):
        import pipes
        return pipes.quote(s)

    def __put_text_back_into_terminal_input_buffer(self,text):
        import fcntl, termios
        for c in text:
            fcntl.ioctl(1, termios.TIOCSTI, c)

    def __change_parent_process_directory(self,dest):
        self.__put_text_back_into_terminal_input_buffer("cd "+ self.__quote_against_shell_expansion(dest)+"\n")

    def exec(self):
        if self.should_show_help(self.__args_list) or not self.__args_list:
            self.help()
            return
        if self.__args_list[-1].startswith('/'):
            dir_prefix = ''
        else:
            dir_prefix = os.getcwd() + '/'
        self.__change_parent_process_directory(dir_prefix + self.__args_list[-1])
