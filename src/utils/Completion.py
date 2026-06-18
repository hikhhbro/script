import os
from command.Shell import Shell
from command.CompTemp import CompTemp
from command.Listdirs import CurFile
from command.Base import Base

class Completion(Base):
    help_summary = "补全系统占位模块，通常无需直接调用。"
    help_usage = "{tool_name} completion [--help]"
    help_options = {
        "--help": "显示当前帮助",
    }

    def __init__(self, args_list=None):
        super().__init__()



