import logging


class MyLogger():
    def __init__(self):
        self.__level = logging.INFO
        self.__init_config = False
        self.NOTSET = logging.NOTSET
        self.DEBUG = logging.DEBUG
        self.INFO = logging.INFO
        self.WARNING = logging.WARNING
        self.ERROR = logging.ERROR
        self.CRITICAL = logging.CRITICAL
        self.debug = logging.debug
        self.info = logging.info
        self.warning = logging.warning
        self.error = logging.error
        self.critical = logging.critical
        

    def tips(self, msg):
        if self.__level > logging.DEBUG:
            print(msg)
        logging.debug(msg)
        
    def input(self, msg,default=""):
        if not default:
            __msg = "%s:" %(msg)
        else:
            __msg = "%s[ 默认:%s ]:" %(msg,default)
        str = input(__msg) or default
        logging.debug(__msg + str)
        return str

        
    def select(self, msg,u_list,default=0):
      for i in range(0,len(u_list)):
        self.tips("%d:%s" % (i, u_list[i]))
      __msg = "%s[ 默认:%s ]:" %(msg,u_list[0] + " 或者 " + str(default))
      ret = input(__msg)
      if ret.isdigit():
          return u_list[int(ret)]
      return ret
          
        
    def config(self, level):
        if not  self.__init_config :
            self.__level = level
            logging.basicConfig(
                level=level, format='%(asctime)s - %(levelname)-7s %(filename)s:%(lineno)-10d %(message)s', datefmt='%Y/%m/%d %H:%M:%S')


Log = MyLogger()
