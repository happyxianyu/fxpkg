from fxpkg import *
from fxpkg.pkgbase import *






libid = 'libsodium'
git_url = 'https://github.com/jedisct1/libsodium.git'


class GflagsMgr(PackageMgrBase):
    def __init__(self, bctx: BuildContext):
        super().__init__(bctx, libid)



        
def get_package_mgr(bctx:BuildContext):
    return GflagsMgr(bctx)


