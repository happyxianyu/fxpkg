import importlib

from .util import Path, path_to_sqlite_url
from .datacls import LibPathInfo, LibConfig, LibDepUnit, LibTriplet, FxHostConfig
from .db import LibDb
from .service import LibService

class FxHostDir:
    def __init__(self, root:Path, create = True, recreate = False):
        root = root.absolute()
        self.attrs = []
        self.lib_subdir_names = lib_subdir_names = ['config', 'download', 'src', 'build', 'install', 'data', 'log', 'cache', 'tmp']
        r = self._record
        r('root', root)
        for name in ['port', 'lib', 'host']:
            r(name, root/name)
        for name in lib_subdir_names:
            r(f'lib_{name}', self.lib/name)
        for name in ['log', 'data']:
            r(f'host_{name}', self.host/name)

        if recreate:
            self.recreate()
        elif create:
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
    def __init__(self, root:Path, reinit=False, debug = False):
        self.dir = FxHostDir(root, recreate=reinit)

        #init port
        self.port =  importlib.import_module('fxpkg.port')
        self.port.__path__.insert(0,self.dir.port.str)

        #init db
        libdb_path = self.dir.host_data/'lib.db'
        self.db = LibDb(path_to_sqlite_url(libdb_path), echo=debug)
        self.config = FxHostConfig()

        #init service
        self.libservice = LibService(self.db.sess)

    def add_port(self, path:Path):
        path.copy_to(self.dir.port, is_prefix=True)
    
    def add_libconfig(self, path:Path, name, version = None):
        dst = self.dir.lib_config/name
        if version:
            dst = dst/version
        path.copy_to(dst,  is_prefix=True)

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
            mp = m.MainPort
            if mp.name is None:
                mp.name = name
            return mp
        
    def make_port(self, name:str):
        return self.get_MainPort(name)(self, self.dir.make_libpathinfo(name))
        
    def install(self, name, version, triplet = None):
        pass

    def install_by_config(self, name, version, config:LibConfig):
        pass

    def install_dependncy(self, dep:LibDepUnit, triplet = None):
        name = dep.name
        port = self.make_port(name)
        ver_int = dep.ver_interval
        if ver_int.b:
            ver = ver_int.b.str
        else:
            ver = port.get_latest_version()
        self._install(port, ver, triplet)

    def _install(self, port, version, triplet = None):
        if triplet == None:
            triplet = self.config.libtriplet

        configs = self.load_libconfigs(port.name, version)
        config = None
        if len(configs):
            triplet.apply_mask(port.get_triplet_mask(version))
            config = LibConfig.get_config_from_list(configs, triplet)
        if config != None:
            config = LibConfig(**triplet.to_dict())
        config = port.make_libconfig(version, config)
        
        self._install_by_config(port, version, config)


    def _install_by_config(self, port, version, config:LibConfig):
        #TODO: check if installed
        info = port.install(version, config)
        #TODO


    def get_libinfos(self, name = None, version = None, triplet = None) -> list:
        pass

    def get_libconfig_file_path(self, name, version, config_name = "default"):
        p1 = self.dir.lib_config/name
        p2 = p1/version

        config_file_name = f'{config_name}.json'
        f1 = p1/config_file_name
        f2 = p2/config_file_name

        for f in [f2, f1]:
            if f.exsits():
                return f

    def load_libconfigs(self, name, version, config_name = 'default'):
        f = self.get_config_file_path(name, version, config_name)
        if f.exists():
            return LibConfig.load_from_file(f)
        return []


    @staticmethod
    def get_libconfig_files_in_dir(dir:Path) -> list:
        if dir.exists():
            return [f for f in dir.file_sons if f.ext == 'json']

    @staticmethod
    def get_libconfig_config_names_in_dir(dir:Path) -> list:
        if dir.exists():
            return [f.stem for f in dir.file_sons if f.ext == 'json']

__all__ = ['FxHost']