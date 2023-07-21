from turtle import update
from command.Shell import Shell
from command.Base import Base
from command.Base import Opt
from command.Log import Log

import os
import re
import pathlib
import json
import xmltodict
import time
import itertools
from datetime import datetime, timedelta



def components(path):
    '''
    Returns the individual components of the given file path
    string (for the local operating system).

    The returned components, when joined with os.path.join(), point to
    the same location as the original path.
    '''
    components = []
    # The loop guarantees that the returned components can be
    # os.path.joined with the path separator and point to the same
    # location:    
    while True:
        (new_path, tail) = os.path.split(path)  # Works on any platform
        components.append(tail)        
        if new_path == path:  # Root (including drive, on Windows) reached
            break
        path = new_path
    components.append(new_path)

    components.reverse()  # First component first
    return components

def longest_prefix(iter0, iter1):
    '''
    Returns the longest common prefix of the given two iterables.
    '''
    longest_prefix = []
    for (elmt0, elmt1) in zip(iter0, iter1):
        if elmt0 != elmt1:
            break
        longest_prefix.append(elmt0)
    return longest_prefix

def common_prefix_path(path0, path1):
    return os.path.join(*longest_prefix(components(path0), components(path1)))

class Build(Base):
    def __init__(self, args_list=None):
        super().__init__(args_list)
        self.__args_list = args_list or ['']
        self.projects_path = self.tool_dir + '/data/build/projects_dir'
        self.__history_project_file_dir = self.tool_dir + '/data/build/history_project/'
        self.__build_tpye_dir = self.tool_dir + '/src/template/build_tpye/'
        self.project_name = None
        if not os.path.exists(self.__history_project_file_dir):
            Shell('mkdir -p ' + self.__history_project_file_dir).exec_system()
        self.__history_project_file_list = os.listdir(
            self.__history_project_file_dir)
        self.projects_list = []
        if not os.path.exists(self.tool_dir + '/data/build'):
            Shell('mkdir -p ' + self.tool_dir + '/data/build').exec_system()
        if os.path.exists(self.projects_path):
            with open(self.projects_path) as f:
                self.projects_list = json.load(f)
        self.cur_dir = os.getcwd() + '/'
        self.build_dic = {}
        self.project_top_dir = self.__get_project_top_dir() 
        self.__lock_file = None
        if self.project_top_dir:
            if os.path.exists(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")):
                with open(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")) as f:
                    self.build_dic.update(json.load(f))
            self.__lock_file = self.project_top_dir + '/.' + os.getenv("SCRIPT_TOOL_NAME") + '_lock'
        self.log_dir =None
        if self.build_dic:
            self.log_dir = "/home/hik/sub_ws/log/" + self.build_dic['project'] + '/'
        Log.debug(self.build_dic)
        self.option_dic = {
            '--init': self.__init,
            '--sync-build-type':self.__sync_build_type
        }
        self.build_cmd = {
            "monking": self.monking,
            "aosp": self.aosp,
            "vela": self.vela,
            "flutter": " ",
            "buildroot": " ",
        }
        self.force_buld = False
    def __set_projects_dir_interaction(self, input_path):
        if not input_path:
            input_path = Log.input("请输入工程顶级目录路径", self.cur_dir)
        else:
            input_path = Log.input(
                "设置工程顶级目录为,需更改请输入(./或者. 为当前路径,回车使用默认)", input_path)
        Log.debug(os.path.abspath(input_path))
        if not os.path.exists(os.path.abspath(input_path)):
            sw = Log.input("输入路径不存在,是否创建此目录(Y/N)", input_path)
            Log.debug("%s,%s" % (sw, input_path))
            if sw == "y" or sw == "Y" or sw == input_path:
                os.makedirs(input_path)
            else:
                Log.tips("退出初始化")
                exit(0)
        return input_path

    def __set_projects_dir(self, input_path):
        input_path = os.path.abspath(input_path)
        if input_path in self.projects_list:
            Log.debug("已存在")
            return True
        if os.path.exists(input_path):
            self.project_top_dir = input_path
            self.projects_list.append(self.project_top_dir)
            Log.debug("历史工程目录:%s" % (self.projects_list))
            with open(self.projects_path, "w+") as f:
                js = json.dumps(self.projects_list, indent=1)
                f.write(js)

    def __read_include_name_frome_xml(self):
        f = open(self.project_top_dir + '/.repo/manifest.xml')
        xml = f.read()
        d = xmltodict.parse(xml)
        f.close()
        return d["manifest"]["include"]["@name"]
# <---------- 自动探测 begin ------->

# TODO: 添加所有编译类型,并由json文件控制
    def __probe_build_type(self):
        Log.debug("开始探测编译工具类型...")

        if os.path.exists(self.project_top_dir + "/monkey_king/monking"):
            Log.tips("探测到编译工具为 monking")
            return "monking"
        Log.error("探测编译类型失败, 请使用手动添加")
        exit()

    def __probe_project_top_dir(self):
        # 探测.repo 目录,工程必须为repo
        Log.debug("开始探测工程顶级目录...")
        p = pathlib.Path(self.cur_dir + "/.repo")
        for up in p.parents:
            if os.path.exists(str(up) + "/.repo"):
                Log.tips("当前工程目录为 %s" % (str(up)))
                self.__set_repo_download_flag(True)
                return str(up)
        Log.debug("探测路径失败,此工程非repo工程")
        return None

# <---------- 自动探测 end ------->

    def __get_log_file(self,name,add_date=True) -> str:
        Shell("mkdir -p %s" % (self.log_dir)).exec_system()
        file_names = os.listdir(self.log_dir)

        # 删除10天前文件
        for eachfile in file_names:
            filename = os.path.join(self.log_dir, eachfile)
            if os.path.isfile(filename):
                lastmodifytime = os.stat(filename).st_mtime
                endfiletime = time.time() - 3600 * 24 * 10
                if endfiletime > lastmodifytime:
                    os.remove(filename)
                    Log.debug("删除文件 %s 成功" % filename)

        if not add_date:
            Log.debug(self.log_dir + name  + '.log')
            return  self.log_dir + name  + '.log'
        times = time.time()
        local_time = time.localtime(times)
        Log.debug(self.log_dir + name + '-' +
                  time.strftime("%d-%H-%M-%S", local_time) + '.log')
        return self.log_dir + name + '-' + time.strftime("%d-%H-%M-%S", local_time) + '.log'

    def __set_repo_download_flag(self, flag):
        if self.project_top_dir and os.path.exists(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")):
            with open(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")) as f:
                Log.debug(self.build_dic)
                self.build_dic.update(json.load(f))
            self.build_dic["repo"] = flag
            with open(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME"), "w+") as f:
                js = json.dumps(self.build_dic, indent=1)
                f.write(js)
        else:
            self.build_dic["repo"] = flag



    def __get_project_top_dir(self):
        Log.debug("获取工程顶级目录")
        # max_len = 0
        # top_dir = ""
        Log.debug(self.projects_list)
        Log.debug(self.cur_dir)
        for item in self.projects_list:
            prefix = common_prefix_path(self.cur_dir,item)
            Log.debug(prefix)
            if prefix in self.projects_list :
                if os.path.exists(prefix + "/.repo"):
                    self.build_dic["repo"] = True
                return prefix
        return None

    def __get_type(self):
        if "type" in self.build_dic.keys():
            return self.build_dic["type"]
        else:
            build_type = self.__probe_build_type()
            if not build_type:
                print("无法探测编译类型,请使用 %s build init -t xxx 手动指定编译类型" %
                      (self.tool_name))
            else:
                self.__init(["-t", build_type])
                return build_type

    def __get_build_targe(self, arg: list):
        # target = self.cur_dir[len(self.project_top_dir)+1:] + (("/" + arg[0]) if arg else "")
        if len(arg) > 0:
            target = arg[0]
        else :
            target = ""
        Log.debug(self.cur_dir + target)
        if  os.path.exists(self.cur_dir + target):
            Log.debug(self.cur_dir[len(self.project_top_dir)+1:])
            Log.debug(target)
            return self.cur_dir[len(self.project_top_dir)+1:] + target , 'dir'
        return target , 'module'

    def __lock(self):
        if self.__lock_file and os.path.exists(self.__lock_file):
            with open(self.__lock_file, "w+") as f:
                tips = "进程号：" + str(os.getpid())
                f.write(tips)
            f.close()
            Log.debug("编译任务开始，已上锁 %s" % (self.__lock_file))

    def __is_locked(self):
        Log.debug(self.__lock_file)
        if self.__lock_file and os.path.exists(self.__lock_file):
            with open(self.__lock_file, encoding="UTF-8") as f:
                Log.tips(f.read())
            f.close()
            return True
        return False

    def __unlock(self):
        if self.__lock_file and os.path.exists(self.__lock_file):
            os.remove(self.__lock_file)
            Log.debug("编译任务结束，已解锁 %s" % (self.__lock_file))
    
    def __parsing_args(self,arg: list):
        if '--force' in arg:
            arg.remove('--force')
            self.force_buld = True
            return "--force"
        if '--toolchain' in arg:
            arg.remove('--toolchain')
            return "--toolchain"
        if '--check' in arg:
          return "--check"

        if "--menuconfig" in arg :
          return "menuconfig"
           
        if "--distclean" in arg:
          return "distclean"
      
        return ""

# <-----编译类型----->

    def monking(self, arg: list):
        s = Shell()
        s.input("cd %s" % (self.project_top_dir))
        s.input("export MINACORE_TOP_DIR=%s/" % (self.project_top_dir))
        long_opt = self.__parsing_args(arg)
        if long_opt == "--toolchain" : 
            if not os.path.exists(self.project_top_dir + '/toolchain'):
                Shell("mkdir -p %s" % (self.project_top_dir + '/toolchain')).exec_system()
                Shell("%s toolchain --source_dir=%s --build_mode=debug --target_os=mi11 --install=%s/toolchain" %
                    (self.build_dic["tool"][0],self.project_top_dir,self.project_top_dir)).exec_system()
            if not os.path.exists(self.project_top_dir + '/.user-projects'):
                user_projects_f_s = Shell()
                user_projects_f_s.input("echo \"\"deps_download_dir: .depPackages\"\" >> %s/.user-projects " %(self.project_top_dir))
                user_projects_f_s.input("echo \"\"default: sources\"\" >> %s/.user-projects " %(self.project_top_dir))
                user_projects_f_s.exec_system()
            return 
        target,target_type = self.__get_build_targe(arg)
        if not os.path.exists(self.project_top_dir + '/out'):
            s.input("%s init -C out --debug -p  %s --target-cpu=%s --sdk=%s/prebuilt/android-toolchain" %
                    (self.build_dic["tool"][0],self.build_dic["project"], self.build_dic["cpu"], self.project_top_dir))
        
        if os.path.exists(self.project_top_dir + '/out/%s/internal/' %(self.build_dic['project']) + target + '/build.sh') and not self.force_buld:
            s.input(self.project_top_dir + '/out/%s/internal/' %(self.build_dic['project']) + target + '/build.sh' )
        else:
            s.input("%s build -C out -p %s %s " %
                    (self.build_dic["tool"][0],self.build_dic["project"], target))
        s.exec_system()

    def aosp(self, arg: list):
        Log.debug("aosp")
        Shell("mkdir -p %s" % (self.log_dir)).exec_system()
        s = Shell()
        s.input("cd %s" % (self.project_top_dir))
        s.input("source build/envsetup.sh")
        s.input("lunch %s-%s" %
                (self.build_dic["project"], self.build_dic["mode"]))
        # Log.debug(matches)
        # Log.debug(file_names)
        self.__parsing_args(arg)
        target ,target_type= self.__get_build_targe(arg)
        Log.debug("编译目标 %s" % (target))
        if not target:
            times = time.time()
            local_time = time.localtime(times)
            Log.debug(self.log_dir)
            s.input("%s dist -j16 | tee %s" %
                    (self.build_dic["tool"][0], self.__get_log_file("full")))
        else:
            # if os.path.exists(self.cur_dir + '/' + 'Android.bp') or os.path.exists(self.cur_dir + '/' + 'Android.mk'):
            ninja_bin = self.project_top_dir + "/prebuilts/build-tools/linux-x86/bin/ninja"
            ninja_build_file = self.project_top_dir + \
                "/out/combined-" + self.build_dic['project'] + ".ninja"
            if os.path.exists(ninja_bin) and os.path.exists(ninja_build_file) and not self.force_buld and target_type == 'module':
                s.input("%s -f %s %s | tee %s" %
                        (ninja_bin, ninja_build_file, target,self.__get_log_file("make",False)))
            elif target_type == 'module' or  self.force_buld :
                s.input("make %s -j16  | tee %s " % (target,self.__get_log_file("make",False)))
            elif target_type == 'dir' :
                s.input("mmm %s | tee %s " % (target,self.__get_log_file("make",False)))
            else:
                Log.tips("编译类型不存在")
                    

        s.exec_system()

    def vela(self,arg: list):
        Log.debug("vela")
        Log.debug(arg)
        build_opt_ = self.__parsing_args(arg)
        if build_opt_ == "--check" and self.build_dic_value("check_tool"):
          s = Shell("cd %s " % (self.cur_dir))
          s.input("git log --pretty=format:%h -n 2")
          commits = s.exe('out')
          commits = commits.splitlines()
          Log.debug(commits)
          check_tool = self.project_top_dir + '/' + self.build_dic_value("check_tool")
          Shell("%s -g %s %s" %(check_tool,commits[0],commits[1])).exec_system()
          exit(1)        
        Shell("mkdir -p %s" % (self.log_dir)).exec_system()
        Log.debug(arg)
        projects = list(set(arg) & set(self.build_dic["projects"]))
        Log.debug(projects)
        if not projects :
          if len(self.build_dic["projects"]) > 1:
            projects = Log.select("请选择编译", self.build_dic["projects"])
          else :
            projects = self.build_dic["projects"][0]
        else :
          projects = projects[0]

        Log.debug(projects)
        s = Shell()
        s.input("cd %s" % (self.project_top_dir))
        
        if projects == "all":
          for i in range(0,len(self.build_dic["projects"]) -1 ):
            s.input("%s vendor/%s/boards/%s %s -j" % (self.build_dic["tool"][0],self.build_dic["project"],self.build_dic_value("configs_path") + self.build_dic["projects"][i],build_opt_))
        else:
          s.input("%s vendor/%s/boards/%s %s -j" % (self.build_dic["tool"][0],self.build_dic["project"],self.build_dic_value("configs_path") + projects,build_opt_))
    
        if self.build_dic_value("pack_tool") and not build_opt_ :
            s.input("%s" % (self.build_dic["pack_tool"]))
        s.exec_system()
          
        
        

    def __get_history_project_args(self, name):
        Log.debug("获取%s历史工程参数" % (name))
        if name in self.__history_project_file_list:
            if os.path.exists(self.__history_project_file_dir + name):
                with open(self.__history_project_file_dir + name) as f:
                    return json.load(
                        f)

    def __set_history_project_args(self, name):
        if name in self.__history_project_file_dir:
            with open(self.__history_project_file_dir + name) as f:
                Log.debug(self.build_dic)
                self.build_dic.update(json.load(f))
                Log.debug(self.build_dic)
        else:
            self.__history_project_file_list.append(name)
        with open(self.__history_project_file_dir + name, "w+") as f:
            js = json.dumps(self.build_dic, indent=1)
            f.write(js)

    def __get_history_project_args_interaction(self, msg=None):
        # 1. 打印已有工程模板选项
        for i in range(len(self.__history_project_file_list)):
            Log.tips("%d:%s" % (i, self.__history_project_file_list[i]))
        if self.project_top_dir and os.path.exists(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")):
            tmp_project_name = Log.input("当前工程名称:%s,是否需要更改" % (self.build_dic["project"]), "N")
            if tmp_project_name != "N" and tmp_project_name != "n":
                Log.debug(tmp_project_name)
                self.__set_history_project_args(tmp_project_name)
                project_name = tmp_project_name
            else:
                return self.build_dic["project"]
        elif not self.__history_project_file_list:
            project_name = Log.input("暂时没有可用工程,请输入工程名称创建")
            self.__set_history_project_args(project_name)
        else:
            project_name = Log.input(
                msg or "请选择工程", not self.__history_project_file_list or self.__history_project_file_list[0]+" or " + "0")
    # 选择已有工程
        Log.debug(project_name)
        if project_name in self.__history_project_file_list:
            Log.debug(self.build_dic)
            self.build_dic.update(
                self.__get_history_project_args(project_name))
            Log.debug(self.build_dic)
        elif project_name.isdigit():
            if int(project_name) < len(self.__history_project_file_list):
                Log.debug(self.build_dic)
                Log.debug(self.__history_project_file_list)
                Log.debug(int(project_name))
                self.build_dic.update(self.__get_history_project_args(
                    self.__history_project_file_list[int(project_name)]))
                Log.debug(self.build_dic)
                project_name = self.__history_project_file_list[int(
                    project_name)]
            else:
                self.__get_history_project_args_interaction("暂时没有%d选项,请重写输入<=%d,或者输入全名" % (
                    int(project_name), len(self.__history_project_file_list)-1))
        # 创建新工程
        else:
            project_name = Log.input("输入工程不存在,是否创建此工程", project_name)
        return project_name

    def __add_history_project(self):
        Log.debug("添加新工程参数")

    def __init_args_handle(self, arg: list):
        Log.debug("处理init 参数")

    def project_has_key(self, key, root=None):
        if not root:
            root = self.build_dic
        return root.__contains__(key)


    def build_dic_value(self, key):
        if self.build_dic.__contains__(key):
            return  self.build_dic[key]
        return  ""


    def __add_build_type_interaction(self):
        Log.tips("暂不支持交互编译类型添加")
        exit()

    def __get_build_type_interaction(self, build_type_list, msg=None):
        if not build_type_list:
            self.__add_build_type_interaction()
        for i in range(len(build_type_list)):
            Log.tips("%d:%s" % (i, build_type_list[i]))
        build_type = Log.input("请选择编译类型", build_type_list[0]+" or " + "0")
        if build_type == "y" or build_type == "Y":
            self.__add_build_type_interaction()
        elif build_type in build_type_list:
            self.build_dic["type"] = build_type
        elif build_type.isdigit():
            if int(build_type) < len(build_type_list):
                self.build_dic["type"] = build_type_list[int(build_type)]
            else:
                self.__get_build_type_interaction(build_type_list, "暂时没有%d选项,请重写输入<=%d,或者输入全名" % (
                    int(build_type), len(build_type_list)-1))
        # 创建新工程
        else:
            self.__get_build_type_interaction(
                build_type_list, "输入编译类型不存在,请重新重新,如需添加新类型,输入:Y/y")
        return build_type

    def __get_input(self,input_list,input):
        if input in input_list:
            return input
        elif input.isdigit():
            if int(input) < len(input_list):
                return input_list[int(input)]
        return None

    def __get_xml_interaction(self):
        if 'xml' in self.build_dic.keys() and isinstance(self.build_dic['xml'],list):
            for i in range(len(self.build_dic['xml'])):
                Log.tips("%d:%s" % (i, self.build_dic['xml'][i]))
            res = Log.input("请选择xml", self.build_dic['xml'][0]+" or " + "0")
            Log.debug(res)
            xml = self.__get_input(self.build_dic['xml'],res)
            Log.debug(xml)
            self.build_dic['xml'] = xml
            
    def __get_branch_interaction(self):
        if 'branch' in self.build_dic.keys() and isinstance(self.build_dic['branch'],list):
            for i in range(len(self.build_dic['branch'])):
                Log.tips("%d:%s" % (i, self.build_dic['branch'][i]))
            res = Log.input("请选择branch", self.build_dic['branch'][0]+" or " + "0")
            Log.debug(res)
            branch = self.__get_input(self.build_dic['branch'],res)
            Log.debug(branch)
            self.build_dic['branch'] = branch

    def __set_build_tpye(self, build_type):
        with open(self.__history_project_file_dir + self.project_name, "w+") as f:
            js = json.dumps(self.build_dic, indent=1)
            f.write(js)

    def __get_build_args(self, build_type):
        if os.path.exists(self.__build_tpye_dir + build_type):
            with open(self.__build_tpye_dir + build_type) as f:
                return json.load(
                    f)

    def __generate_project_file(self):
        tmp_dic = {}
        print(self.project_top_dir)
        if os.path.exists(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")):
            with open(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME")) as f:
                tmp_dic = json.load(f)
        Log.debug(self.build_dic)
        tmp_dic.update(self.build_dic)
        Log.debug(tmp_dic)
        with open(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME"), "w+") as f:
            js = json.dumps(tmp_dic, indent=1)
            f.write(js)

    def __download(self):
        s = Shell()
        branch = ""
        xml = ""
        if self.build_dic["branch"] :
          branch = "-b " + self.build_dic["branch"]
        if self.build_dic["xml"]:
          xml = "-m " + self.build_dic["xml"]
        s.input_and_echo("repo init -u %s %s %s %s" %
                         (self.build_dic["url"], branch, xml ,self.build_dic["repo_tool"]))
        if s.exec_system() != 0:
            Log.tips("repo init 失败")
            exit()
        s.input_and_echo("repo sync -j4 -d -c --no-tag")
        if s.exec_system() != 0:
            Log.tips("repo sync 失败")
            exit()

    def __input_list(self,k):
        i = 0;
        tmp_list = []
        while True:
          s = "输入y退出，请输入第%d个%s" %(i,k)
          i = i + 1
          ret = Log.input(s)
          if ret == 'y' :
            break
          tmp_list.append(ret)
        return tmp_list

    def __input_str(self,k):
        return Log.input("请输入%s" %(k))

    def __input_bool(self,k):
      return bool(Log.input("请输入%s" %(k)))

    def __init_config(self):
        Log.debug(self.project_top_dir)
        for k,v in self.build_dic.items():
          if not v:
            if isinstance(v,list) :
                self.build_dic[k] = self.__input_list(k)
            elif isinstance(v,str) :
                self.build_dic[k] = self.__input_str(k)
            elif isinstance(v,bool) :
                self.build_dic[k] = self.__input_bool(k)

    def __init(self, arg: list):
        Log.debug("开始初始化")
    # 1. 处理传入的参数
        if arg:
            self.__init_args_handle(arg)

    # 2. 识别工程顶级目录 或者获取工程模板参数
        self.project_name = self.__get_history_project_args_interaction()
        input_dir = self.project_top_dir
        if not input_dir:
            input_dir = self.__probe_project_top_dir() or self.project_name

    # 3. 设置工程目录
        self.__set_projects_dir(self.__set_projects_dir_interaction(input_dir))
        Log.debug(self.build_dic)
        
    # 初始化空目录后,加锁
        if not self.__is_locked():
            self.__lock()
        
    # 4. 获取或设置编译类型
        build_type_list = os.listdir(self.__build_tpye_dir)
        if not self.project_has_key("type"):
            self.__set_build_tpye(
                self.__get_build_type_interaction(build_type_list))
        Log.debug(self.build_dic)
        
    
        # self.__get_xml_interaction()
        # self.__get_branch_interaction()
        # Log.debug(self.build_dic)

    # 5. 初始化编译参数
        self.__init_config()
        Log.debug(self.build_dic)

    # 6. 生成编译参数文件
        # self.build_dic.update(build_args)
        self.__generate_project_file()
        Log.debug(self.build_dic)

    # 7. 下载源码
        if self.build_dic["repo"]:
            self.__download()

    # def rootfs(self, arg: list):
    #     if  self.project_has_key('roofts'):
          


    def __sync_build_type(self,arg: list):
      Log.debug("sync build type")
      build_dic_tmp = {}

      build_dic_tmp.update(dict.fromkeys(self.build_dic,""))

      with open(self.__history_project_file_dir + self.build_dic["type"]) as f:
          build_dic_tmp.update(json.load(f))
          
      with open(self.__history_project_file_dir + self.build_dic["type"], "w+") as f:
        js = json.dumps(build_dic_tmp, indent=1)
        f.write(js)
      
      build_dic_tmp.update(self.build_dic)
      
      with open(self.project_top_dir + '/.build.' + os.getenv("SCRIPT_TOOL_NAME"), "w+") as f:
          js = json.dumps(build_dic_tmp, indent=1)
          f.write(js)
        
        

    def __start_build(self, arg: list):
        if self.__get_type() in self.build_cmd.keys():
            self.build_cmd[self.__get_type()](arg)

    def exec(self):
        # if self.__is_locked():
        #     Log.tips("已经有编译任务在执行")
        #     return
        # self.__lock()
        # try:
        if self.__args_list[0] in self.option_dic.keys():
            self.option_dic[self.__args_list[0]](self.__args_list[1:])
        else:
            self.__start_build(self.__args_list[0:])
    # except Exception as e:
    #     Log.error(e)
    # finally:
        # self.__unlock()

    def help(self, arg: list):
        print(
            "%s build init option[ --download=\"-u url -b branch -m xml -j thread -d dir\" |" % (self.tool_name))
        print("                          -b build_type | -p product   ] : 工程初始化")
        print("--download=\"\", -d 表示下载到指定的目录, 不用-d ,会下载到当前目录,--download=dir 初始化一个空目录,不下载")
        print("--download=和-d 不能同时用,可以和-p,-b同时用")


    def __get_history(self):
        return ["com.android.wifi","com.android.tethering","services","framework-minus-apex"] 

    def _opt(self):
        if self.build_dic_value("type") == "vela":
          return Opt(["--menuconfig","--distclean","--check"] + self.build_dic["projects"] + list(self.option_dic.keys()))
        elif not self.build_dic:
            return Opt(['--init'],False)
        return Opt(self.__get_history(),True)
      