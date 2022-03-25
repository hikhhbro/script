import os
# from __future__ import division
class Compile:
    def __init__(self,filepath):
        self.filepath = filepath
        self.readlines=[]
        self.writelines=[]
        self.rootpath = os.path.abspath(os.path.dirname(__file__)) + "/"
        self.operator = {'<_describe>':get_describe,'<_get_options>':get_options,'#<main>':get_main}
    def get_describe(self):
        print(get_describe)
        # pass
    def get_options(self):
        pass
    def get_main(self):
        pass
    def get_other(self):
        pass
    def handle(self):
        file = open(self.rootpath + self.filepath) 
        for line in file:
            pass
        file.close()
    



if __name__ == '__main__':
    comp = Compile("script/test")
    # print(comp.rootpath)
    comp.operator.get("<_describe>")
    # print(__file__)
    # Path=os.path.abspath(os.path.dirname(__file__))
    # print(Path)