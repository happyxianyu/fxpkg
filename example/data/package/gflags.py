from fxpkg import *
from fxpkg.pkgbase import *



libid = 'gflags'
class GflagsMgr(CMakePkgMgr):
    def __init__(self, bctx: BuildContext):
        super().__init__(bctx, 'gflags')

    def version_to_tag(self, version) -> str:
        return f'v{version}'


def get_package_mgr(bctx:BuildContext):
    return GflagsMgr(bctx)


