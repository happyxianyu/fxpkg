# from .librepo import LibRepo
from fxpkg.util import Path
from .util import DirectDict, path_to_sqlite_url
import importlib
from fxpkg.db import LibDb

from fxpkg.common.globalval import resource_path

def init_fxpkg_root(root_path, overwrite = False, is_prefix = False):
    #set src and dst
    src = resource_path/'pkg_root'
    dst = Path(root_path)

    if is_prefix: dst = dst/'fxpkg'
    if dst.exists():
        if overwrite:
            dst.remove()
        else:
            return dst
    dst.mkdir()
    src.copy_sons_to(dst)
    return dst

class FxpkgHost:
    def __init__(self, root_path, debug = False):
        root_path = Path(root_path)

        #set path info
        self.path = path = DirectDict()
        path.root = root_path
        for name in ['tmp', 'cache', 'install', 'port', 'data']:
            setattr(path, name, root_path/name)
        for name in ['download', 'src', 'build', 'other']:
            setattr(path, f'{name}_cache', path.cache/name)

        #init port
        self.port =  importlib.import_module('fxpkg.port')
        self.port.__path__.insert(0,path.port.to_str())

        self.db = LibDb(path_to_sqlite_url(self.path.data/'libdb.db'), echo=debug)

    def add_port(self, port_path):
        port_path = Path(port_path)
        port_path.copy_to(self.path.port, is_prefix=True)

    def import_port(self, name):
        try:
            m = importlib.import_module('fxpkg.port.'+name)
        except ModuleNotFoundError:
            return

        if hasattr(m, 'MainPkg'):
            return m

    

__all__ = ['FxpkgHost', 'init_fxpkg_root']