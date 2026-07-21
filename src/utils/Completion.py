from command.Base import Base

class Completion(Base):
    def __init__(self, args=None):
        super().__init__(args)
        self.meta("补全系统占位模块，通常无需直接调用。", args="[--help]")
