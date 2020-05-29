from .libinfo_repo import LibRepo
from .util import Path

class FxpkgHost:
    def __init__(self, root_path = 'pkg_root'):
        self.workpath = workpath = Path(root_path)
        self.repo = LibRepo(workpath/'data')

    def install_dependency(self, dependency):
        pass

    def request_lib(self, d:dict) ->list:
        pass

    def check_exist(self):
        pass

__all__ = ['FxpkgHost']