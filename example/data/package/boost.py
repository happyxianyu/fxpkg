from fxpkg import *
from fxpkg.pkgbase import *



libid = 'boost'
git_url = 'https://github.com/boostorg/boost.git'

class GflagsMgr(CMakePkgMgr):
    def __init__(self, bctx: BuildContext):
        super().__init__(bctx, libid, git_url)

    def version_to_tag(self, version) -> str:
        return f'boost-{version}'

    async def install(self, config: InstallConfig = None):
        bctx = self.bctx
        repo_path = self.repo_path
        build_path = self.build_path
        install_path = self.install_path
        run_cmd_async = bctx.run_cmd_async
        run_heavy_proc = bctx.run_heavy_proc
        await run_heavy_proc(run_cmd_async(f'./b2 --prefix={install_path} --build-dir={build_path} install', cwd=repo_path))

    async def build(self, config: InstallConfig = None):
        bctx = self.bctx
        repo_path = self.repo_path
        build_path = self.build_path
        install_path = self.install_path
        run_cmd_async = bctx.run_cmd_async
        run_heavy_proc = bctx.run_heavy_proc
        await run_heavy_proc(run_cmd_async(f'./b2 --prefix={install_path} --build-dir={build_path}', cwd=repo_path))


    async def configure(self, config: InstallConfig = None):
        bctx = self.bctx
        repo_path = self.repo_path
        run_cmd_async = bctx.run_cmd_async
        run_heavy_proc = bctx.run_heavy_proc
        run_light_proc = bctx.run_light_proc
        await run_light_proc(run_cmd_async('./bootstrap.bat', cwd=repo_path))
        await run_heavy_proc(run_cmd_async(f'./b2 headers', cwd=repo_path))

        
    async def download(self, config: InstallConfig = None):
        bctx = self.bctx
        repo_path = self.repo_path
        run_shellscript_async = bctx.run_shellscript_async
        run_light_download = bctx.run_light_download

        await super().download(config)
        await run_light_download(run_shellscript_async(f'''
git submodule init
git submodule update --recursive --depth=1
''', cwd=repo_path))

        



def get_package_mgr(bctx:BuildContext):
    return GflagsMgr(bctx)



