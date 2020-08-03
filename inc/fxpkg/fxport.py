from .fxhost import FxpkgHost
from .datacls import PortInfo, LibConfig, PortConfig
from .util import DirectDict


class FxPort:
    info:PortInfo = PortInfo(name = 'None')

    def __init__(self, host: FxpkgHost, config:PortConfig):
        self.host = host
        self.config = config
        self.init()

    def init(self):
        pass

    def make_libconfig(self, config: LibConfig = None, option:str = None) ->LibConfig:
        return config

    def install(self, config: LibConfig):
        '''return lib info'''
        return None



__all__ = ['FxPort']