from .datacls import LibPathInfo

class FxPort:
    name:str = 'unknown'
    def __init__(self, host, lib_path_info:LibPathInfo):
        self.host = host
        self.lib_path_info = lib_path_info

__all__ = ['FxPort']