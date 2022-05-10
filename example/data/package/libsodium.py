from fxpkg import *
from fxpkg.pkgbase import *






libid = 'libsodium'
git_url = 'https://github.com/jedisct1/libsodium.git'


class LibsodiumMgr(GitPkgMgr):
    def __init__(self, bctx: BuildContext):
        super().__init__(bctx, libid, git_url)

    async def build(self, bctx):
        pass

        
def get_package_mgr(bctx:BuildContext):
    return LibsodiumMgr(bctx)


