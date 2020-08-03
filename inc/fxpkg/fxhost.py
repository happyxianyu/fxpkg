# from .librepo import LibRepo
import importlib

from .util import Path, DirectDict, path_to_sqlite_url, update_attr2
from .db import MainDb
from .common.globalval import resource_path
from .datacls import LibConfig,PortConfig
from .dao import LibInfoDao
from .service import *
from .common import FxConfig

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

class FxpkgHostPathConfig(FxConfig):
    def __init__(self, root_path:Path):
        super().__init__()
        self.root = root_path
        for name in ['log', 'tmp', 'cache', 'install', 'port', 'data']:
            #set root sub path
            setattr(self, name, root_path/name)
        for name in ['download', 'src', 'build', 'other']:
            #set cache sub path
            setattr(self, name, self.cache/name)
        for name in ['install', 'build']:
            #set log sub path
            setattr(self, f'{name}_log', self.log/name)
        for name in ['host', 'port']:
            #set data sub path
            setattr(self, f'{name}_data', self.data/name)
        
    def create_path(self):
        attrs = self.get_attrs()
        for attr in attrs:
            getattr(self, attr).mkdir()


class FxpkgHost:
    def __init__(self, root_path, debug = False):
        root_path = Path(root_path)

        self.path = path = FxpkgHostPathConfig(root_path)
        path.create_path()

        #init port
        self.port =  importlib.import_module('fxpkg.port')
        self.port.__path__.insert(0,path.port.to_str())

        #init database and service
        self.maindb = MainDb(path_to_sqlite_url(path.host_data/'maindb.db'), echo=debug)
        self.libinfo_service = LibInfoService(self.maindb)

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
        return MainPort(self, self.make_port_config(name))

    def install(self, name:str, config:LibConfig):
        port = self.make_mainport(name)

        config = port.make_libconfig(config)
        #TODO: add config hook

        #TODO: install dependency
        config = port.install(config)

        if config:
            service = self.libinfo_service
            config.name = port.info.name
            service.store_libinfo_by_object(config)
            #TODO: store lib information
        else:
            pass
            #TODO: handle failing



    def make_port_config(self, name) -> PortConfig:
        path = self.path
        config = PortConfig(
            log_path = path.port_log/name,
            download_path = path.download/name,
            src_path = path.src/name,
            build_path = path.build/name,
            install_path=path.install/name,
            data_path=path.port_data/name
        )
        return config

    def complete_libconfig(self, config:LibConfig, port):
        lconf,pconf = config, port.config
        name = port.info.name

        subdir_name = lconf.make_dir_name()
        install_path = pconf.install_path/subdir_name

        updated_path = dict(
            log_path = pconf.log_path/subdir_name,

            download_path = pconf.download_path,
            src_path = pconf.src_path,
            build_path = pconf.build_path/subdir_name,

            install_path = install_path,
            inc_path = install_path/'inc'/name,
            lib_path = install_path/'lib',
            cmake_path = install_path/'cmake',
            data_path = pconf.data_path/subdir_name
        )

        update_attr2(config, updated_path)
    

__all__ = ['FxpkgHost', 'init_fxpkg_root']