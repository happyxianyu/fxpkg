from cbutil import load_module

from .librepo import LibRepo
from .path import Path

class FxpkgHost:
    def __init__(self, root_path = 'pkg_root'):
        self.root_path = root_path = Path(root_path)
        self.repo = LibRepo(root_path/'install_info')

    def install_dependency(self, dependency):
        pass

    def request_lib(self, d:dict) ->list:
        pass

    def check_exist(self):
        pass

__all__ = ['FxpkgHost']