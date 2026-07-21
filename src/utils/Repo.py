try:
    import xmltodict
except ImportError:
    xmltodict = None
import os
from command.Shell import Shell
from command.Base import Base

class Repo(Base):
    def __init__(self, args=None):
        super().__init__(args)
        self.meta("比较两个 repo manifest XML 的项目差异。", args="<left.xml> <right.xml> [--same-name|--all]")
        self.command_tree.long('--same-name', '比较同名项目的差异')
        self.command_tree.long('--all', '显示全部 revision 差异')
        self.short_options = self.args[2] if len(self.args) > 2 else ''
        self.xml_project = []
        if len(self.args) >= 2:
            self.xml_project = [
                self.__read_project_frome_xml(self.args[0]),
                self.__read_project_frome_xml(self.args[1]),
            ]
    def __read_project_frome_xml(self, xml_path):
        if xmltodict is None:
            raise RuntimeError("xmltodict is required for repo XML parsing")
        with open(xml_path) as f:
            xml = f.read()
        d = xmltodict.parse(xml)
        return d["manifest"]["project"]
    
    def __get_map(self,xml_project):
        __dict = {}
        for i  in xml_project[0]:
            if "@name" in i:
                __dict[i["@revision"]] = [i["@name"],0]
        for i  in xml_project[1]:
            if "@name" in i:
                if i["@revision"] in __dict:
                    del __dict[i["@revision"]]
                else:
                    __dict[i["@revision"]] = [i["@name"],1]
        return __dict
          
    
    
    def __get_set(self,xml_project):
        return {item["@name"] for item in xml_project if "@name" in item}

    def __get_diff(self,set_1,set_2):
        list_tmp = []
        out_list = []
        list_1_2 = sorted(set_1 ^ set_2,key=lambda x: x[0])
        for left, right in zip(list_1_2, list_1_2[1:] + [('', '')]):
            if left[0] == right[0]:
                list_tmp += list(left + right)
            else:
                if not list_tmp:
                    out_list.append(left)
                else:
                    tmp = list(set(list_tmp))
                    tmp.sort(key = list_tmp.index)
                    out_list.append(tuple(tmp))
                    list_tmp.clear()
        return out_list
    
    def __print(self,out_list):
        max_name_len = 0
        max_revision_len = 0
        times = 0
        for i in out_list:
            if len(i) > 2 :
                if len(i[0]) > max_name_len:
                    max_name_len = len(i[0])
                if len(i[1]) > max_revision_len:
                    max_revision_len = len(i[1])
        tile = "name"    
        print(f"name : {self.args[0]} <---> {self.args[1]}")
        for i in out_list:
            if len(i) > 2 :
                times = times +1
                print(f"{times}: {i[0]:{max_name_len}} : {i[1]:{max_revision_len}} <---> {i[2]:{max_revision_len}}")      
        
    def __same_name_diff_revision(self):
        # out_list = self.__get_diff(self.__get_set(self.xml_project[0]),self.__get_set(self.xml_project[1]))
        set1 = self.__get_set(self.xml_project[0])
        set2 = self.__get_set(self.xml_project[1])
        set_1_2 = set1 & set2
        set_1_m = set1 - set_1_2
        set_2_m = set2 - set_1_2
        print(set_2_m)
        # self.__print(out_list)

    def __all_diff_revision(self):
        out_list = self.__get_diff(self.__get_set(self.xml_project[0]),self.__get_set(self.xml_project[1]))
        __map = self.__get_map(self.xml_project)
        max_name_len = 0
        max_revision_len = 0
        for i in out_list:
            if len(i) > 0 :
                if len(i[0]) > max_name_len:
                    max_name_len = len(i[0])
                if len(i[1]) > max_revision_len:
                    max_revision_len = len(i[1])
        tile = "name"    
        print(f"name : {self.args[0]} <---> {self.args[1]}")
        times = 0
        for i in out_list:
            times = times +1
            if len(i) > 2 :
                l = i[2] if __map[i[1]][1] else i[1]
                r = i[1] if __map[i[1]][1] else i[2]
                print(f"{times}: {i[0]:{max_name_len}} : {l:{max_revision_len}} <---> {r:{max_revision_len}}")  
            else:
                
                if i[1] in __map:
                    l = " " if __map[i[1]][1] else i[1]
                    r = i[1] if __map[i[1]][1] else " "
                    print(f"{times}: {i[0]:{max_name_len}} : {l:{max_revision_len}} <---> {r:{max_revision_len}}")   
    def exec(self):
        if self.should_show_help(self.args):
            self.help()
        elif len(self.args) < 3 or not self.xml_project:
            self.help()
        elif self.short_options == "--same-name":
            self.__same_name_diff_revision()
        elif self.short_options == "--all":
            self.__all_diff_revision()
        else:
            self.help()
