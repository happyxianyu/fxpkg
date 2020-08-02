from .fxhost import FxpkgHost
from .util import DirectDict
from dataclasses import dataclass


basic_config_field = ['cache_path' , 'src_path', 'build_path', 'tool_path', 'install_path', 'tmp_path']


@dataclass
class PkgConfig(DirectDict):
    '''
    build option
    '''
    arch:str = 'x64'
    build_type:str = 'debug'
    platform:str = 'windows'
    version:str = None

    inc_path:str = None
    lib_path:str = None
    bin_path:str = None
    cmake_path:str = None

    use_exist_target:bool = True   
    #if this is true and there is existed installed target, package will not build it again.

    # extra:DirectDict = None
    # #provided by package


@dataclass
class PkgInfo(DirectDict):
    '''
    Describe basic package info
    '''
    name:str
    

class FxPackage:
    def __init__(self, host:FxpkgHost):
        self.host = host

    def get_extra_config(self, option = 'common') -> DirectDict:
        '''
        Options:
        common
        agreesive
        conservative
        '''

    def begin(self, config):
        self.config = config

    def download(self):
        pass

    def extract_src(self):
        pass

    def build(self):
        pass

    def install(self):
        pass

    def end(self):
        '''return information'''
        pass

__all__ = ['FxPackage']