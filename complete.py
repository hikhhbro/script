import os
import sys
# import Compile
class Complete:
    def __init__(self,asgs=[]):
        self.end = asgs[-1]
        self.asgs = asgs
        self.asgs.pop()
        self.file = self.to_file()
        self.input = {}
        self.out = {}
        self.public_com = {'hikrun' : ['--rm','--code']}
        self.setspace = {True : 'compopt +o nospace',False :'compopt -o nospace'}
        self.end_dic = {'n': False, 'y': True}
        self.root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
        self.root_dir_len = len(self.root_dir)
        
    def last_input(self): # hikrun  wiz/w  -> wiz/w  
        return self.asgs[-1]

    def last_2_input(self):
        if len(self.asgs) > 2 :
            return self.asgs[-2]
        else :
            return None

    def to_file(self):  # wiz/w -> [wiz,w]
        if self.last_2_input() == 'hikrun' and self.last_input()[0] == '-' :
            return self.public_com
        else:
            i = self.last_input().rfind('/') 
            if i >= 0:
                file = {'prefix' : '' , 'path' : self.last_input()[:i] , 'name' : self.last_input()[i+1:]}
            else :
                file = {'prefix' : '' , 'path' : '', 'name' : self.last_input()}
            return  file



    def set_prefix(self,prefix): # [script,wiz,w]
        self.file['prefix'] = prefix
    
    def set_path(self,path):
        self.file['path'] = path
    
    def set_name(self,name):
        self.file['name'] = name

    def get_prefix(self): # [script,wiz,w]
        return self.file['prefix']
    
    def get_path(self):
        return self.file['path']
    
    def get_name(self):
        return self.file['name']

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
        prefix = ''
        for root ,dirs,files in os.walk(self.root_dir+'/'+name):
            for d in dirs:
                if d[0] != '.':
                    self.input['{}/'.format(d)] = root + '/' + d
            for file in files:
                if self.isexecutable(file) :
                    self.input[file] = root + '/' + file 
            prefix = root[self.root_dir_len+1:]        
            l = prefix.find('/')
            if l >= 0 :
                prefix = prefix[:l]
            break
        return prefix
        
    def get_input(self):
        return self.input

    def matching_file(self,indir):
        out = {}
        for k,v in indir.items():
            l = len(self.get_name())
            if l < len(k) and self.get_name() == k[0:l] :
                out[k] = v
        if not out and (self.end == 'y' or '/' == self.asgs[-1][-1] ):
            out = self.get_input()
        return out

    def matching_opt(self,indir):
        out = {}
        return out

    def file_path(file):  #wiz/w    wi  wiz/
        i = self.last_input().rfind('/')
        self.last_input()[:]
        return file[1]
    
    def file_name(file):
        return file[0]

    def compgen(self):
        if  len(self.asgs) == 3 and '-' in file :
            # self.out = self.matching(file, self.public_com)
            pass
        else:
            self.out = self.matching_file(self.get_input())
        # if not self.out and self.isend() :
        #     pytime = os.path.getmtime(os.path.join(root, sc)) 
        #     txttime = os.path.getmtime(os.path.join(root, txt)) 

    def getlsspace(self):
        if  len(self.out) == 1 and list(self.out.keys())[0][-1] == '/':
            return False
        else:
            return True
        
    def isend(self): # has space -> true  
        return self.end_dic[self.end]

    def find_files_dirs(self,file_dir):
        for item in file_dir:
            prefix = self.find_files(item)
            if prefix != '':
                self.set_prefix(prefix)
            

#todo 设计成字典调用
    def set_complete(self) -> bool :
        if self.isend() :
            if self.last_input() == 'hikrun' :
                file_dir = ["script",'company'] 
                self.matching_file()  #self.matching_file() 
            elif self.last_input() == '--code' or self.last_input() == '-c': 
                file_dir = ["script",'company'] 
                self.matching_file()  #self.matching_file() 
            else :
                file_dir = ["script",'company'] 
                self.matching_file()  #self.matching_file() 
        else :
            if '-' in self.last_input() :
                self.matching_opt() #self.matching_file() 
            else :
                self.matching_file()  #self.matching_file() 
        return self.getlsspace()


        # for i in range(len(file_dir)):
        #     file_dir[i] = file_dir[i] + "/" + self.get_path()
        # self.find_files_dirs(file_dir)
        # self.compgen()
      
if __name__ == '__main__':
    # com = Complete(sys.argv)
    com = Complete(['hikrun','wiz/w','n'])
    com.set_out(com.set_complete())