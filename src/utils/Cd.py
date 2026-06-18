import os
from command.Listdirs import CurFile
from command.Base import Base, Opt
class Cd(Base):
    help_summary = "把 cd 命令写回当前终端输入缓冲区，实现父 shell 跳转。"
    help_usage = "{tool_name} cd <目录>"
    help_options = {
        "--help": "显示当前帮助",
    }
    help_examples = [
        "hikrun cd shell",
        "hikrun cd /tmp",
    ]

    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.__args_list = self.normalize_args(args_list)
        self.add_dic = { }

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
        
    def _opt(self):
        curfile = CurFile(self.__args_list[-1])
        return curfile.get_file_opt()