class Trie:
    def __init__(self, root: dict = None):
        self.root = root or {}
        self.end = -1
        self.is_change = False

    def get_node(self, key: str = None, date: dict = None, tip: str = None):
        return [date or {}, tip]

    def insert(self, arg_list: list):
        self.is_change = False
        node = self.root
        for arg in arg_list:
            if arg not in node:
                node[arg] = self.get_node()
                self.is_change = True
            node = node[arg][0]
        return self.is_change

    def search(self, arg_list: list):
        node = self.root
        for arg in arg_list:
            if arg not in node:
                return False
            node = node[arg][0]
        return node if arg_list else self.root

    def delete(self, arg_list: list):
        node = self.root
        for i, arg in enumerate(arg_list):
            if arg not in node:
                return False
            if i == len(arg_list) - 1:
                del node[arg]
                return True
            node = node[arg][0]
        return False
