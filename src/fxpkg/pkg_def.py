from .libhost import LibHost
basic_config_field = ['cache_path' , 'src_path', 'build_path', 'tool_path', 'install_path', 'tmp_path']
class PackageConfig:
    def __init__(self):
        self._data = dict.fromkeys(basic_config_field)
    
    def __getattribute__(self, x):
        return self._data[x]

    def __setattr__(self,a,v):
        self._data[a] = v


class Package:
    def __init__(self, host:LibHost):
        self.host = host

    def get_config(self, config:PackageConfig, option = 'common'):
        '''Options:
        common
        agreesive
        conservative
        '''
        return config

    def begin(self, config:PackageConfig):
        self.config = config

    def download(self):
        pass

    def build(self):
        pass

    def install(self):
        pass

    def end(self) -> dict:
        '''return information'''
        pass

    def is_latest(self) -> bool:
        pass
