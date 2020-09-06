import importlib

from .util import Path
from .datacls import LibPathInfo

class FxHostDir:
    def __init__(self, root:Path, create = True):
        self.attrs = []
        self.lib_subdir_names = lib_subdir_names = ['config', 'cache', 'install', 'data', 'log', 'tmp']
        r = self._record
        r('root', root)
        for name in ['port', 'lib', 'host']:
            r(name, root/name)
        for name in lib_subdir_names:
            r(f'lib_{name}', self.lib/name)
        for name in ['log', 'data']:
            r(f'host_{name}', self.host/name)
        if create:
            self.create()


    def _record(self, attr, path):
        setattr(self, attr, path)
        self.attrs.append(attr)

    def create(self):
        for attr in self.attrs:
            getattr(self, attr).mkdir()
    
    def recreate(self):
        self.root.remove()
        self.create()

    def make_libpathinfo(self, name:str) -> LibPathInfo:
        return LibPathInfo(**{k:getattr(self,f'lib_{k}')/name for k in self.lib_subdir_names})


class FxHost:
    def __init__(self, root:Path):
        self.dir = FxHostDir(root)

        #init port
        self.port =  importlib.import_module('fxpkg.port')
        self.port.__path__.insert(0,self.dir.port.str)

    def add_port(self, path:Path):
        path.copy_to(self.dir.port, is_prefix=True)

    def import_port(self, name:str):
        try:
            m = importlib.import_module('fxpkg.port.'+name)
        except ModuleNotFoundError:
            return

        if hasattr(m, 'MainPort'):
            return m

    def get_MainPort(self, name:str):
        m = self.import_port(name)
        if m:
            return m.MainPort
        
    def make_port(self, name:str):
        return self.get_MainPort(name)(self, self.dir.make_libpathinfo(name))
        


__all__ = ['FxHost']