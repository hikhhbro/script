import json
import os
class Json:
    def __init__(self, file_path):
        self.path = file_path
    
    def str_to_json(self,text) :
        return text
    
    def write_json(self,text):
        json_data = self.str_to_json(text)
        with open(self.path ,"w+") as wf:
            js = json.dumps(json_data,indent=1)
            wf.write(js)
    def read_json(self):    
        with open(self.path) as rf:
            json_data = json.load(rf)
        return json_data
      

    def write(self,text):
        json_data = self.str_to_json(text)
        with open(self.path ,"w+") as wf:
            js = json.dumps(json_data,indent=1)
            wf.write(js)
    def read(self,default=None):    
        with open(self.path) as rf:
            json_data = json.load(rf)
        if default and not json_data:
          return default
        return json_data