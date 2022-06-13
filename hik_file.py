import os
class CurFile():
    def __init__(self,script_dir = os.getcwd()):
        self.__file_opt = []
        self.__script_dir = script_dir + '/'
        self.__dic_opt = {
            'all': self.__all,
            'exe_file':self.__isexecutable,
            'alldir':self.__alldir,
            'dir':self.__dir,
        }
    def __find_files(self,postfix='',is_=['all']):
        for root, dirs, files in os.walk(self.__script_dir + postfix):
            for item in is_:
                self.__file_opt = self.__file_opt +  self.__dic_opt[item](dirs,files)
            break
    def __get_dir(self,postfix):
        l = postfix.rfind('/')
        if l < 0:
            return ''
        else:
            return postfix[0:l+1]
    def get_file_opt(self,postfix='',is_=['all']):
        if postfix == None:
            postfix = ''
        else:
            postfix = self.__get_dir(postfix)
        self.__find_files(postfix,is_)
        return self.__file_opt


    def __all(self,dirs,files):
        return files + self.__dir(dirs,files)

    def __isexecutable(self,dirs,files):
        tmp = []
        for file in files:
            if  '.' not in file:
                tmp.append(file)
        return tmp

    def __dir(self,dirs,files):
        r = []
        for d in dirs:
            if d[0] != '.' :
                r.append(d + '/')
        return r
    def __alldir(self,dirs,files):
        r = []
        for d in dirs:
            r.append(d + '/')
        return r

