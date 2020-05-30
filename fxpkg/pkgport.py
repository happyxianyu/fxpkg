from .host import FxpkgHost
from .DirectDict import DirectDict
basic_config_field = ['cache_path' , 'src_path', 'build_path', 'tool_path', 'install_path', 'tmp_path']

class PackageConfig(DirectDict):
    '''
    Config is for installing
    Provided by host as input
    '''

class PackageInfo(DirectDict):
    '''
    Info is for storing
    Provided by package as return value
    '''

class Package:
    def __init__(self, host:FxpkgHost):
        self.host = host

    def get_config(self, config:PackageConfig, option = 'common'):
        '''
        Options:
        common
        agreesive
        conservative
        '''
        return config

    def begin(self, config:PackageConfig):
        self.config = config

    def download(self):
        pass

    def extract_src(self):
        pass

    def build(self):
        pass

    def install(self):
        pass

    def end(self) -> PackageInfo:
        '''return information'''
        pass

__all__ = ['PackageConfig', 'PackageInfo', 'Package']