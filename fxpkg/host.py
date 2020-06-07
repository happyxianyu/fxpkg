from .librepo import LibRepo
from .path import Path
from .DirectDict import DirectDict

def init_fxpkg_root(root_path, overwrite = False):
    root_path = Path(root_path)
    if root_path.exists():
        if overwrite == True:
            root_path.remove()
        else:
            return
    root_path.mkdir()
    src_root_path = Path(__file__).prnt/'pkg_root'
    src_root_path.copy_sons_to(root_path)

class FxpkgHost:
    def __init__(self, root_path):
        root_path = Path(root_path)
        self.path = path = DirectDict(root = root_path)
        for name in ['install_info', 'port','src', 'install',  'cache',  'temp']:
            path.get_dict()[name] = root_path/'name'
        self.port =  __import__('fxpkg.port')
        self.port.__path__.insert(0,path.port)
        self.repo = LibRepo(self.path.install_info)

    def update_port(self, port_path):
        port_path = Path(port_path)
        port_path.copy_to(self.path.port, is_prefix=True)

    def install_dependency(self, dependency):
        pass

    def request_lib(self, d:dict) ->list:
        pass

    def check_exist(self):
        pass

__all__ = ['FxpkgHost', 'init_fxpkg_root']