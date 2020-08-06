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
        '''
        Should fill not None basic attributes to install
        '''
        return config

    def install(self, config: LibConfig):
        '''Return lib info'''
        return None

    def get_support_uninstall_key(self, key):
        '''Return support uninstall'''
        return None

    def uninstall(self, key):
        #TODO
        return None



__all__ = ['FxPort']