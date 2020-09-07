from .datacls import LibPathInfo, LibConfig
from .model import LibInfo

class FxPort:
    name:str = 'unknown'

    def __init__(self, host, lib_path_info:LibPathInfo):
        self.host = host
        self.lib_path_info = lib_path_info

    def make_config(self, version, config:LibConfig) -> LibConfig:
        '''fill default config key and value'''
        return config

    def install(self, version, config:LibConfig) -> LibInfo:
        pass

    def get_latest_version(self) -> str:
        pass

    def get_triplet_mask(self, version) -> int:
        '''
        platform: 1
        arch: 2
        build_type: 4
        '''
        return 7



__all__ = ['FxPort']