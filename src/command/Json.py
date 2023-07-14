import json
import os
class Json:
    def __init__(self, file_path=''):
        self.file = os.getenv('SCRIPT_TOP_DIR') + '/' + file_path
    
    def str_to_json(self,text) :
        return text
    
    def write_json(self,text):
        json_data = self.str_to_json(text)
        with open(self.file ,"w+") as wf:
            js = json.dumps(json_data,indent=1)
            wf.write(js)
    def read_json(self):    
        with open(self.file) as rf:
            json_data = json.load(rf)
        return json_data
      
