from hik_file import CurFile
class hikrun_cd():
    def __init__(self, args_list=None):
        self.__args_list = args_list or []
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
        if self.__args_list[-1][0] == '/':
            dir_prefix = ''
        else :
            dir_prefix = os.getcwd() + '/'
        self.__change_parent_process_directory(dir_prefix + self.__args_list[-1] )
        
    def _opt(self):
        curfile = CurFile()
        return curfile.get_file_opt(self.__args_list[-1])