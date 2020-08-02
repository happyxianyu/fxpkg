# from .librepo import LibRepo
import importlib

from .util import Path, DirectDict, path_to_sqlite_url, setattr_by_dict
from .db import LibDb
from .common.globalval import resource_path
from .datacls import LibConfig,PortConfig

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
        for name in ['log', 'tmp', 'cache', 'install', 'port', 'data']:
            setattr(path, name, root_path/name)
        for name in ['download', 'src', 'build', 'other']:
            setattr(path, name, path.cache/name)
        for name in ['install_log', 'build_log']:
            setattr(path, name, path.log/name)

        #init port
        self.port =  importlib.import_module('fxpkg.port')
        self.port.__path__.insert(0,path.port.to_str())

        self.db = LibDb(path_to_sqlite_url(self.path.data/'libdb.db'), echo=debug)

    def add_port(self, port_path):
        port_path = Path(port_path)
        dst = self.path.port/port_path.name
        if dst.exists():
            dst.remove()
        port_path.copy_to(dst)

    def import_port(self, name):
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

    def make_mainport(self, name:str):
        MainPort = self.get_MainPort(name)
        return MainPort(self)

    def install(self, name:str, config:LibConfig):
        port = self.make_mainport(name)

        config = port.make_default_libconfig(config)
        #TODO: change config hook
        config = port.complete_libconfig(config)
        config = port.install(config)
        #TODO: store lib information

    def make_port_config(self, port) -> PortConfig:
        path = self.path
        name = port.info.name
        config = PortConfig(
            log_path = path.build_log/name,
            download_path = path.download/name,
            src_path = path.src/name,
            build_path = path.build/name,
            install_path=path.install/name
        )
        return config

    def complete_libconfig(self, config:LibConfig, port):
        name = port.info.name
        pconf:PortConfig = port.port_config

        subdir_name = config.make_dir_name()

        src_dict = {
            'log_path' : pconf.log_path/subdir_name,

            'download_path' : pconf.download_path,
            'src_path' : pconf.src_path,
            'build_path' : pconf.build_path/subdir_name,

            'inc_path' : pconf.build_path/subdir_name/'inc'/name,
            'lib_path' : pconf.build_path/subdir_name/'lib',
            'bin_path' : pconf.build_path/subdir_name/'bin',
            'cmake_path' : pconf.build_path/subdir_name/'cmake'
        }

        setattr_by_dict(config, src_dict, cond = lambda k: not hasattr(config, k) or getattr(config, k) == None)
    

__all__ = ['FxpkgHost', 'init_fxpkg_root']