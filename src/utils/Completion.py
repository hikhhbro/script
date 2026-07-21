import os
from command.Shell import Shell
from command.CompTemp import CompTemp
from command.Listdirs import CurFile
from command.Base import Base

class Completion(Base):
    def __init__(self, args_list=None):
        super().__init__()
        self.meta("补全系统占位模块，通常无需直接调用。", args="[--help]")

