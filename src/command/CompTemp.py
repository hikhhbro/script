from command.Json import Json
from command.Trie import Trie

class CompTemp():
    def __init__(self,args_list = None):
        self.file = '/data/.complete.json'
        try:
            self.trie = Trie(Json(self.file).read_json())
        except:
             Json(self.file).write_json({})
             self.trie = {}
        self.args =  args_list[1:] if  args_list else []
    
    def get(self):
        return self.trie.search(self.args)

    def set(self,arg_list:list = None):
        if not arg_list:
          if self.trie.insert(self.args) :
              Json(self.file).write_json(self.trie.root)
          return False
        else :
            for item in arg_list:
                status = self.trie.insert([item])
            if status:
                Json(self.file).write_json(self.trie.root)
                return True
            else:
                return False

    def delete(self,arg_list:list = None):
        self.trie.delete(arg_list)
        Json(self.file).write_json(self.trie.root)
                