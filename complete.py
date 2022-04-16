import os
import sys
class Complete:
    def __init__(self,asgs=[]):
        self.end = asgs[-1]
        self.asgs = asgs
        self.asgs.pop()
        self.input = []
        self.out = []
        self.public_com = ['--rm','--code']
        self.setspace = {True : 'compopt +o nospace',False :'compopt -o nospace'}
        self.end_dic = {'n': False, 'y': True}
        self.root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
        
    def set_out(self,sw:bool):
        print(self.setspace[sw])
        print(' '.join(self.out))
    
    def isexecutable(self,file):
        if '.sh' in file or '.' not in file :
            return True
        else:
            return False
    
    def file_name(self,name=''):
        for root ,dirs,files in os.walk(self.root_dir+'/'+name):
            for d in dirs:
                if d[0] != '.':
                    self.input.append([ 'root','{}/'.format(d)])
            for file in files:
                if self.isexecutable(file) :
                    self.input.append([ 'root','{}'.format(file)])
            break
        
    def get_input(self):
        out = []
        for item in self.input:
            out.append(item[-1])
        return out
            
    def matching(self,file,inlist):
        out = []
        for it in inlist:
            l = len(file[-1])
            if l < len(it) and file[-1] == it[0:l] :
                if len(file) > 1:
                    out.append(''.join(file[0:-1])+it)
                else:
                    out.append(it)    
        if not out and (self.end == 'y' or '/' == self.asgs[-1][-1] ):
            out = self.get_input()
        return out
    
    def compgen(self,file):
        if  len(self.asgs) == 3 and '-' in file[-1] :
            self.out = self.matching(file, self.public_com)
        else:
            self.out = self.matching(file, self.get_input())

    def getlsspace(self):
        if len(self.out) == 1 and self.out[0][-1] == '/':
            return False
        else:
            return True
        
    def isend(self):
        return self.end_dic[self.end]

    def find_files_dirs(self,file_dir):
        for item in file_dir:
            self.file_name(item)

    def set_complete(self) -> bool :
        file_dir = ["script",'company'] 
        file = [self.asgs[-1]]
        if '/' in self.asgs[-1] and not self.isend() :
            file =  [self.asgs[-1][:self.asgs[-1].rfind('/')] + '/']
            for i in range(len(file_dir)):
                file_dir[i] = file_dir[i] + "/" + file[0]
            file.append(self.asgs[-1][self.asgs[-1].rfind('/')+1:])
            if file[-1] == '' :
                file.pop()
        self.find_files_dirs(file_dir)
        self.compgen(file)
        return self.getlsspace()
      
if __name__ == '__main__':
    com = Complete(sys.argv)
    # com = Complete(['hikrun','wiz/w','n'])
    com.set_out(com.set_complete())