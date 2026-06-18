import os


class CurFile():
    def __init__(self, init_dir=None):
        self.__file_opt = []
        if init_dir:
            self.__cur_dir = os.path.abspath(init_dir) + '/'
        else:
            self.__cur_dir = os.getcwd() + '/'
        self.__dic_opt = {
            'all': self.__all,
            'exe_file': self.__isexecutable,
            'alldir': self.__alldir,
            'dir': self.__dir,
        }

    def __find_files(self, postfix='', is_=None):
        self.__file_opt = []
        is_ = is_ or ['all']
        target_dir = os.path.normpath(self.__cur_dir + postfix)
        if not os.path.isdir(target_dir):
            return
        for root, dirs, files in os.walk(target_dir):
            for item in is_:
                self.__file_opt = self.__file_opt + self.__dic_opt[item](root, dirs, files)
            break

    def __get_dir(self, postfix):
        index = postfix.rfind('/')
        if index < 0:
            return ''
        return postfix[0:index + 1]

    def get_file_opt(self, postfix='', is_=None, exclude=None):
        exclude = exclude or []
        if postfix is None:
            postfix = ''
        else:
            postfix = self.__get_dir(postfix)
        self.__find_files(postfix, is_)
        for item in exclude:
            if item in self.__file_opt:
                self.__file_opt.remove(item)
        return self.__file_opt

    def __all(self, root, dirs, files):
        return files + self.__dir(root, dirs, files)

    def __looks_like_script(self, path, file):
        _, ext = os.path.splitext(file)
        if not ext or ext == '.sh':
            return True
        try:
            with open(path, 'rb') as handle:
                return handle.read(2) == b'#!'
        except OSError:
            return False

    def __isexecutable(self, root, dirs, files):
        out = []
        for file in files:
            path = os.path.join(root, file)
            if (
                os.path.isfile(path)
                and os.access(path, os.X_OK)
                and self.__looks_like_script(path, file)
            ):
                out.append(file)
        return out

    def __dir(self, root, dirs, files):
        out = []
        for directory in dirs:
            if directory and directory[0] != '.':
                out.append(directory + '/')
        return out

    def __alldir(self, root, dirs, files):
        return [directory + '/' for directory in dirs]
