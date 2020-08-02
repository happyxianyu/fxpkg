from .fxhost import FxpkgHost
from .datacls import PortInfo, LibConfig
from .util import DirectDict


class FxPort:
    info:PortInfo = PortInfo(name = 'None')

    def __init__(self, host: FxpkgHost):
        self.host = host
        self.port_config = host.make_port_config(self)
        self.init()

    def init(self):
        pass

    def make_default_libconfig(self, config: LibConfig = None) ->LibConfig:
        return config

    def complete_libconfig(self, config: LibConfig) ->LibConfig:
        self.host.complete_libconfig(config,self)
        return config

    def install(self, config: LibConfig):
        '''return lib info'''
        return None



__all__ = ['FxPort']