from dataclasses import dataclass
from fxpkg.util import Path

@dataclass
class PortInfo:
    '''
    Describe package info
    '''
    name:str

@dataclass
class PortConfig:
    log_path:Path = None
    download_path:Path = None 
    src_path:Path = None
    build_path:Path = None
    install_path:Path = None

@dataclass
class LibConfig:
    '''
    build option
    '''
    version:str = None
    arch:str = 'x64'
    build_type:str = 'debug'
    platform:str = 'windows'
    
    log_path:Path = None

    download_path:Path = None 
    src_path:Path = None
    build_path:Path = None

    inc_path:Path = None
    lib_path:Path = None
    bin_path:Path = None
    cmake_path:Path = None

    use_exist_target:bool = True   
    #if this is true and there is existed installed target, package will not build it again.

    dependency:list = None

    # extra:DirectDict = None
    # #provided by package
    def make_dir_name(self):
        l = []
        for k in ['version', 'arch', 'build_type', 'platform']:
            v = getattr(self, k)
            if v == None:
                l.append('')
            else:
                l.append(v)
        return '-'.join(l)


__all__ = ['LibConfig', 'PortInfo', 'PortConfig']