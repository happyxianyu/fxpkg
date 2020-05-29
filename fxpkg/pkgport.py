from .host import FxpkgHost
basic_config_field = ['cache_path' , 'src_path', 'build_path', 'tool_path', 'install_path', 'tmp_path']


class DictWrapClass:
    def __init__(self, *args, **kwargs):
        super().__setattr__('_data', dict(*args,**kwargs))
    
    def __getattr__(self, x):
        return self._data[x]

    def __setattr__(self,a,v):
        self._data[a] = v

    def get_dict(self):
        return self._data

class PackageConfig(DictWrapClass):
    '''
    Config is for installing
    Provided by host as input
    '''

class PackageInfo(DictWrapClass):
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