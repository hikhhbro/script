from command.Json import Json
from command.Trie import Trie


class CompTemp():
    def __init__(self, args_list=None):
        self.file = 'data/.complete.json'
        try:
            root = Json(self.file).read_json()
        except Exception:
            root = {}
            Json(self.file).write_json(root)
        self.trie = Trie(root)
        self.args = args_list[1:] if args_list else []

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
            Json(self.file).write_json(self.trie.root)
        return changed

    def delete(self, arg_list: list = None):
        if self.trie.delete(arg_list or []):
            Json(self.file).write_json(self.trie.root)
            return True
        return False
