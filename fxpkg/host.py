# from .librepo import LibRepo
from .path import Path
from .DirectDict import DirectDict
import importlib
from .pkgrepo import PkgRepo

def init_fxpkg_root(root_path, overwrite = False, is_prefix = False):
    if is_prefix:
        dst = Path(root_path)/'fxpkg'
    else:
        dst = Path(root_path)
    if dst.exists():
        if overwrite:
            dst.remove()
        else:
            return dst
    dst.mkdir()
    src = Path(__file__).prnt/'pkg_root'
    src.copy_sons_to(dst)
    return dst

class FxpkgHost:
    def __init__(self, root_path):
        root_path = Path(root_path)
        self.path = path = DirectDict(root = root_path)
        for name in ['data', 'port','src', 'install',  'cache',  'temp']:
            path.get_dict()[name] = root_path/name
        self.port =  importlib.import_module('fxpkg.port')
        self.port.__path__.insert(0,path.port.to_str())
        self.repo = PkgRepo(self.path.data)

    def update_port(self, port_path):
        port_path = Path(port_path)
        port_path.copy_to(self.path.port, is_prefix=True)

    def get_port(self, name):
        try:
            m = importlib.import_module('fxpkg.port.'+name)
        except ModuleNotFoundError:
            return
        try:
            m.MainPkg
        except AttributeError:
            return
        return m

    def get_mainpkg(self, name):
        return self.get_port(name).MainPkg

    def install_dependency(self, dependency):
        pass

    def request_lib(self, d:dict) ->list:
        pass

    def check_exist(self):
        pass

__all__ = ['FxpkgHost', 'init_fxpkg_root']