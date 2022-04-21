import os
import sys
import compile

class Complete:
    def __init__(self,asgs=[]):
        self.end = asgs[-1]
        self.asgs = asgs
        self.asgs.pop()
        self.out = {}
        self.hikrun = ['--rm','--code']
        self.setspace = {True : 'compopt +o nospace',False :'compopt -o nospace'}
        self.end_dic = {'n': False, 'y': True}
        self.root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
        self.root_dir_len = len(self.root_dir)
        
    def last_input(self): # hikrun  wiz/w  -> wiz/w  
        return self.asgs[-1]

    def last_2_input(self):
        if len(self.asgs) > 1 :
            return self.asgs[-2]
        else :
            return None

    def set_out(self,sw:bool): 
        print(self.setspace[sw])
        print(' '.join(list(self.out.keys())))
    
    def isexecutable(self,file): 
        if '.sh' in file or '.' not in file :
            return True
        else:
            return False

    def to_compile_path(path):
        return self.root_dir + '.compile/' + path[self.root_dir_len:]

    def find_files(self,name=''):
        file_dir = {}
        for root ,dirs,files in os.walk(self.root_dir+'/'+name):
            for d in dirs:
                if d[0] != '.':
                    file_dir['{}/'.format(d)] = root + '/' + d
            for file in files:
                if self.isexecutable(file) :
                    file_dir[file] = root + '/' + file 
            break
        return file_dir

    def get_file_name(self,file):
        return file[self.last_input().rfind('/') :]

    def matching_file(self,dir_list,file=None):
        file_dir = self.find_files_dirs(dir_list)
        out = {}
        if (file_dir) and (file != None) and (file[-1] != '/') :
            for k,v in file_dir.items():
                l = len(self.get_file_name(file))
                if l < len(k) and self.get_file_name(file) == k[0:l] :
                    out[k] = v
        else :
            out = file_dir
        if len(out) == 1 and file == None and (file[-1] != '/'):
            self.compile_file(list(out.values())[0])
        self.out = out

    def matching_opt(self,opt_list):
        for i in opt_list :
            if self.last_input() in i:
                self.out[i] = None

    def getlsspace(self):
        if  len(self.out) == 1 and list(self.out.keys())[0][-1] == '/':
            return False
        else:
            return True
        
    def isend(self): # has space -> true  
        return self.end_dic[self.end]

#todo 增加同名文件提示和选择
    def find_files_dirs(self,file_list):
        file_d = {}
        for item in file_list:
            file_d.update(self.find_files(item))   # file_d = {}
        return file_d

    def compile_file(self,file):
        comp = compile(file)


#todo 设计成字典调用
    def set_complete(self) -> bool :
        if self.isend() :
            if self.last_input() == 'hikrun' or self.last_input() == '--code' or self.last_input() == '-c' :
                dir_list = ["script",'company'] 
                self.matching_file(dir_list)  #self.matching_file()
            else :
                pass
                # file_dir = ["script",'company'] 
                # self.matching_file()  #self.matching_file() 
        else :
            if '-' in self.last_input() :
                self.matching_opt(self.hikrun) #self.matching_file() 
            elif self.last_2_input() == 'hikrun' or self.last_2_input() == '--code' or self.last_2_input() == '--rm':
                dir_list = ["script",'company'] 
                self.matching_file(dir_list,self.last_input())  #self.matching_file() 
            else :
                self.out = {}
        return self.getlsspace()

      
if __name__ == '__main__':
    com = Complete(sys.argv)
    # com = Complete(['hikrun','test1','n'])
    com.set_out(com.set_complete())