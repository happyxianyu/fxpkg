from fxpkg import *
from fxpkg.pkgbase import *



libid = 'boost'
git_url = 'https://github.com/boostorg/boost.git'

class GflagsMgr(CMakePkgMgr):
    def __init__(self, bctx: BuildContext):
        super().__init__(bctx, libid, git_url)

    def version_to_tag(self, version) -> str:
        return f'boost-{version}'

    async def install(self):
        self._set_config(config)
        config = self.config
        bctx = self.bctx
        repo_path = self.repo_path
        build_path = self.build_path
        install_path = self.install_path
        log_path = self.log_path
        run_cmd_async = bctx.run_cmd_async
        run_heavy_proc = bctx.run_heavy_proc
        run_shellscript_async = bctx.run_shellscript_async
        await run_heavy_proc(run_shellscript_async(f".\\b2 --prefix={install_path} --build-dir={build_path} install > {log_path/'install.txt'}", cwd=repo_path))

    async def build(self):
        self._set_config(config)
        config = self.config
        bctx = self.bctx
        repo_path = self.repo_path
        build_path = self.build_path
        log_path = self.log_path
        install_path = self.install_path
        run_cmd_async = bctx.run_cmd_async
        run_heavy_proc = bctx.run_heavy_proc
        run_shellscript_async = bctx.run_shellscript_async
        await run_heavy_proc(run_shellscript_async(f'''.\\b2 --prefix={install_path} --build-dir={build_path} > {log_path/'build.txt'}''', cwd=repo_path))


    async def configure(self):
        self._set_config(config)
        config = self.config
        bctx = self.bctx
        repo_path = self.repo_path
        log_path = self.log_path
        run_shellscript_async = bctx.run_shellscript_async
        run_cmd_async = bctx.run_cmd_async
        run_heavy_proc = bctx.run_heavy_proc
        run_light_proc = bctx.run_light_proc
        await run_light_proc(run_shellscript_async(f".\\bootstrap.bat > {log_path/'config.txt'}", cwd=repo_path))
        await run_light_proc(run_shellscript_async(f".\\b2 headers >> {log_path/'config.txt'}", cwd=repo_path))

        
    async def download(self, config: InstallConfig = None):
        self._set_config(config)
        config = self.config
        bctx = self.bctx
        repo_path = self.repo_path
        version = config.version
        run_shellscript_async = bctx.run_shellscript_async
        run_light_download = bctx.run_light_download
        tag = self.version_to_tag(version)

        await super().download(config)
        await run_light_download(run_shellscript_async(f'''
git submodule init
git submodule update --recursive --depth 1
git submodule foreach --recursive git fetch --depth=1 origin +refs/tags/{tag}:refs/tags/{tag}
git submodule foreach --recursive git checkout tags/{tag}
''', cwd=repo_path))

        



def get_package_mgr(bctx:BuildContext):
    return GflagsMgr(bctx)



