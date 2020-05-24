from libinfo_repo import LibInfoRepo
from util import Path

class LibHost:
    def __init__(self, workdir = 'libinfo'):
        self.workpath = workpath = Path(workdir)
        self.repo = LibInfoRepo(workpath/'data')

    def install_dependency(self, dependency):
        pass

    def request_lib(self, d:dict) ->list:
        pass

    def check_exist(self):
        pass
