import json
from aiofile import AIOFile
from fxpkg.common import *
from fxpkg.helpler import *
from fxpkg.buildctx import *
from .gpm import *


class CMakePkgMgr(GitPkgMgr):
    def __init__(self, bctx: BuildContext, libid: str, git_url=None):
        super().__init__(bctx, libid, git_url)

    async def request(self, config: InstallConfig = None):
        self._set_config(config)
        config = self.config
        libid = self.libid
        git_url = self.git_url
        build_type = config.build_type
        version = config.version
        repo_path = self.repo_path
        build_path = self.build_path
        install_path = self.install_path
        bctx = self.bctx
        run_light_proc = bctx.run_light_proc
        run_cmd_async = bctx.run_cmd_async
        run_heavy_proc = bctx.run_heavy_proc

        for p in (build_path, install_path):
            p.mkdir()

        # download
        await self.download()

        # configure
        await self.configure()

        # build
        await self.build()

        # install
        await self.install()
        return self.get_install_entry()



    async def install(self):
        config = self.config
        build_type = config.build_type
        repo_path = self.repo_path
        build_path = self.build_path
        install_path = self.install_path
        bctx = self.bctx
        run_light_proc = bctx.run_light_proc
        run_cmd_async = bctx.run_cmd_async
        self._set_config(config)
        await run_light_proc(run_cmd_async(f'cmake --build {build_path.quote} --target install --config {build_type}', cwd=repo_path))


    async def build(self):
        config = self.config
        repo_path = self.repo_path
        build_path = self.build_path
        bctx = self.bctx
        run_cmd_async = bctx.run_cmd_async
        run_heavy_proc = bctx.run_heavy_proc
        await run_heavy_proc(run_cmd_async(f'cmake --build {build_path.quote}', cwd=repo_path))


    async def configure(self):
        await super().configure()
        config = self.config
        repo_path = self.repo_path
        build_path = self.build_path
        install_path = self.install_path
        bctx = self.bctx
        run_light_proc = bctx.run_light_proc
        run_cmd_async = bctx.run_cmd_async
        cmake_presets = make_cmake_presets(config, install_path)
        version = config.version
        tag = self.version_to_tag(version)
        async with AIOFile(repo_path/'CMakeUserPresets.json', 'w') as fw:
            await fw.write(json.dumps(cmake_presets, ensure_ascii=False, indent=4))
        assert (repo_path/'CMakeUserPresets.json').exists()
        await run_light_proc(run_cmd_async(f'cmake . -B {build_path.quote} --preset=real', cwd=repo_path))



