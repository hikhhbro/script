from command.Json import Json
from command.Trie import Trie


class CompTemp():
    def __init__(self, args=None):
        self.file = 'data/.complete.json'
        self.store = Json(self.file).ensure({})
        root = self.store.read({})
        self.trie = Trie(root)
        self.args = args[1:] if args else []

    def __save(self):
        self.store.write(self.trie.root)

    def get(self, item=None):
        if not item:
            return self.trie.search(self.args)
        return self.trie.search([item])

    def set(self, arg_list: list = None):
        changed = False
        if not arg_list:
            changed = self.trie.insert(self.args)
        else:
            for item in arg_list:
                changed = self.trie.insert([item]) or changed
        if changed:
            self.__save()
        return changed

    def delete(self, arg_list: list = None):
        if self.trie.delete(arg_list or []):
            self.__save()
            return True
        return False
