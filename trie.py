class Trie:
    def __init__(self,root:dict = None):
        self.root = root or {}
        self.end = -1
        self.is_change = False
    def get_node(self,key:str = None,date:dict = None,tip:str = None):
        return [date or {},tip]
    
    def insert(self, arg_list:list):
        self.is_change = False
        node = self.root
        for arg in arg_list:
            child =  node if node.__contains__(arg) else {}
            if not child :
                node[arg] = self.get_node()
                self.change = True
            node = node[arg][0]
        return self.is_change