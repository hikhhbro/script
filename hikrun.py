import os
import sys

from shell import Shell

root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
dir_list = ["script", 'company']


class Code():
    def __init__(self, args=None):
        self.__dic = {
            '-c': self.__company_file,
            '-a': self.__adb_file,
            '-adb-sync': self.__adb_sync_file,
            None: self.__open_file
        }
        self.__args_list = args or []

    def __code_file(self, f):
        if os.path.isfile(f):
            Shell('code ' + f).exe()

        s = Shell()
        s.input('cp ' + root_dir + '/' + '.template ' + f)
        s.input("code " + f)
        s.exe()

    def __company_file(self, args_list):
        f = root_dir + '/' + 'company/' + ''.join(args_list[-1])
        self.__code_file(f)

    def __script_file(self, args_list):
        f = root_dir + '/' + 'script/' + ''.join(args_list[-1])
        self.__code_file(f)

    def __find_file(self, args_list):
        for item in dir_list:
            f = root_dir + '/' + item + '/' + args_list[-1]
            if os.path.isfile(f):
                return f

    def __open_file(self, args_list):
        f = self.__find_file(args_list)
        if f:
            self.__code_file(f)
        else:
            self.__script_file(args_list)

    def __adb_dest_file(self, f):
        return f.replace('/', '#')

    def __adb_src_file(f):
        return f.replace('#', '/')

    def __adb_file(self, args_list):
        srcfile = ''.join(args_list[-1])
        dire = root_dir + '/adb_file/' + self.__adb_dest_file(srcfile)
        s = Shell()
        s.input('adb pull ' + srcfile + ' ' + dire)
        s.input('code ' + dire)
        s.exe()

    def __adb_sync_file(self, args_list):
        s = Shell()
        for root, dirs, files in os.walk(root_dir + '/adb_file/'):
            s.input('adb push ' + root + '/' +
                    files[0] + ' ' + self.__adb_src_file(files[0]))
            s.input('rm  ' + root + '/' + files[0])
            s.exe()
            break

    def run(self):
        if self.__args_list[0] in self.__dic:
            self.__dic[self.__args_list[0]](self.__args_list[1:])
        else:
            self.__dic[None](self.__args_list)


class Rm():
    def __init__(self, args_list=None):
        self.__args_list = args_list or []

    def run(self):
        if self.__args_list[0] == '-c':
            self.__args_list.pop(0)
            dir_tmp = 'company/'
        else:
            dir_tmp = 'script/'
        f = root_dir + '/' + dir_tmp + ''.join(self.__args_list[-1])
        resycle = root_dir + '/' + dir_tmp + \
            '.resycle/' + ''.join(self.__args_list[-1])
        Shell('mv ' + f + ' ' + resycle).exe()


run = {
    '--code': lambda args_list:  Code(args_list).run(),
    '--rm': lambda args_list: Rm(args_list).run()
}


def get_probe(f):
    index = f.rfind('/')
    if index != -1:
        return f[index+1:] + '_probe'
    return f + '_probe'


def get_file_path(f):
    for item in dir_list:
        if os.path.isfile(root_dir + '/' + item + '/' + f):
            return root_dir + '/' + item + '/' + f
    return None


def get_compile_path(f):
    for item in dir_list:
        if os.path.isfile(root_dir + '/' +
                          '.compile/' + item + '/' + f + '/' + f):
            return root_dir + '/' + '.compile/' + \
                item + '/' + f + '/' + f


def main():
    if sys.argv[1] in list(run.keys()):
        run[sys.argv[1]](sys.argv[2:])
    else:
        s = Shell()
        f = get_compile_path(sys.argv[1])
        s.input('. ' + f)
        s.input(get_probe(sys.argv[1]) + ' ' + ''.join(sys.argv[2:]))
        print(s.exe())


if __name__ == '__main__':
    main()
