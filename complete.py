import os
class Complete:
    def __init__(self,asgs=''):
        self.asgs = asgs
        self.out = 'y '
        self.root_dir = os.getenv('HIK_SCRIPT_TOP_DIR')
    def set_complete(self):
        self.file_name("script")
    def set_out(self):
        print(self.out)
    def file_name(self,name=''):
        for root ,dirs,files in os.walk(self.root_dir+'/'+name):
            for d in dirs:
                if d[0] != '.':
                    self.out =self.out +d + '/ '  
            self.out += ' '.join(files)
            break

if __name__ == '__main__':
    com = Complete()
    com.set_complete()
    com.set_out()
