from libhost import LibHost
basic_config_field = ['cache_dir' , 'src_dir', 'build_dir', 'tool_dir', 'install_dir']
class PackageConfig:
    def __init__(self):
        self._data = dict.fromkeys(basic_config_field)
    
    def __getattribute__(self, x):
        return self._data[x]

    def __setattr__(self,a,v):
        self._data[a] = v


class Package:
    def __init__(self, host:LibHost):
        pass

    def get_config(self, config:PackageConfig):
        pass

    def begin(self, config:dict):
        pass

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
