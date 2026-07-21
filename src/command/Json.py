import json
import os


class Json:
    def __init__(self, file_path):
        if file_path and file_path[0] == '/':
            self.path = file_path
        else :
            self.path = os.path.join(os.getenv('SCRIPT_TOP_DIR') or os.getcwd(), file_path)

    @staticmethod
    def merge(default, data):
        if not isinstance(default, dict):
            return data
        if not isinstance(data, dict):
            return default
        merged = dict(data)
        for key, value in default.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = Json.merge(value, merged[key])
        return merged

    def ensure_parent(self):
        parent = os.path.dirname(self.path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        return self

    def ensure(self, default=None):
        if not os.path.exists(self.path):
            self.write(default or {})
        return self
    
    def str_to_json(self,text) :
        return text
    
    def write_json(self,text):
        json_data = self.str_to_json(text)
        self.ensure_parent()
        with open(self.path ,"w+", encoding='utf-8') as wf:
            js = json.dumps(json_data,indent=1,ensure_ascii=False)
            wf.write(js)
    def read_json(self):    
        with open(self.path, encoding='utf-8') as rf:
            json_data = json.load(rf)
        return json_data
      

    def write(self,text):
        json_data = self.str_to_json(text)
        self.ensure_parent()
        with open(self.path ,"w+", encoding='utf-8') as wf:
            js = json.dumps(json_data,indent=1,ensure_ascii=False)
            wf.write(js)
    def read(self,default=None, merge=False):
        if not os.path.exists(self.path):
            self.write(default or {})
            return default or {}
        with open(self.path, encoding='utf-8') as rf:
            json_data = json.load(rf)
        if default and (merge or not json_data):
          json_data = self.merge(default, json_data)
        return json_data

    def update(self, data=None, **kwargs):
        current = self.read({})
        if not isinstance(current, dict):
            current = {}
        if data:
            current.update(data)
        if kwargs:
            current.update(kwargs)
        self.write(current)
        return current

    def get(self, key, default=None):
        data = self.read({})
        if not isinstance(data, dict):
            return default
        return data.get(key, default)

    def set(self, key, value):
        data = self.read({})
        if not isinstance(data, dict):
            data = {}
        data[key] = value
        self.write(data)
        return value
