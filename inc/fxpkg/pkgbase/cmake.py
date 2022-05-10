import json
from aiofile import AIOFile
from fxpkg.common import *
from fxpkg.helpler import *
from fxpkg.buildctx import *
from .base import *


class CMakePkgMgr(PackageMgrBase):
    def __init__(self, bctx: BuildContext, libid: str, git_url=None):
        if git_url is None:
            git_url = f'https://github.com/{libid}/{libid}.git'

        self.bctx = bctx
        self.libid = libid
        self.git_url = git_url

    def set_config(self, config: InstallConfig):
        self.config = config
        build_type = config.build_type
        version = config.version

        self.repo_path = config.download_path
        self.build_path = (config.build_path/version/build_type).absolute()
        self.install_path = config.install_path/version/build_type
        self.log_path = config.log_path/version/build_type

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
        install_entry = InstallEntry()
        install_entry.install_path = install_path
        install_entry.include_path = install_path/'include'
        install_entry.lib_path = install_path/'lib'
        install_entry.cmake_path = install_path/'lib/cmake'
        return install_entry

    def get_install_entry(self, config:InstallConfig = None) -> InstallEntry:
        self._set_config(config)
        config = self.config
        install_path = self.install_path
        install_entry = InstallEntry()
        install_entry.install_path = install_path
        install_entry.include_path = install_path/'include'
        install_entry.lib_path = install_path/'lib'
        install_entry.cmake_path = install_path/'lib/cmake'
        return install_entry


    async def install(self, config:InstallConfig = None):
        self._set_config(config)
        config = self.config
        build_type = config.build_type
        repo_path = self.repo_path
        build_path = self.build_path
        install_path = self.install_path
        bctx = self.bctx
        run_light_proc = bctx.run_light_proc
        run_cmd_async = bctx.run_cmd_async
        self._set_config(config)
        await run_light_proc(run_cmd_async(f'cmake --build {build_path} --target install --config {build_type}', cwd=repo_path))


    async def build(self, config:InstallConfig = None):
        self._set_config(config)
        config = self.config
        repo_path = self.repo_path
        build_path = self.build_path
        bctx = self.bctx
        run_cmd_async = bctx.run_cmd_async
        run_heavy_proc = bctx.run_heavy_proc
        await run_heavy_proc(run_cmd_async(f'cmake --build {build_path}', cwd=repo_path))


    async def configure(self, config: InstallConfig = None):
        self._set_config(config)
        config = self.config
        repo_path = self.repo_path
        build_path = self.build_path
        install_path = self.install_path
        bctx = self.bctx
        run_light_proc = bctx.run_light_proc
        run_cmd_async = bctx.run_cmd_async
        cmake_presets = make_cmake_presets(config, install_path)
        async with AIOFile(repo_path/'CMakeUserPresets.json', 'w') as fw:
            await fw.write(json.dumps(cmake_presets, ensure_ascii=False, indent=4))
        assert (repo_path/'CMakeUserPresets.json').exists()
        await run_light_proc(run_cmd_async(f'cmake . -B {build_path} --preset=real', cwd=repo_path))


    async def download(self, config: InstallConfig = None):
        self._set_config(config)
        config = self.config
        libid = self.libid
        git_url = self.git_url
        version = config.version
        repo_path = self.repo_path

        bctx = self.bctx
        run_cmd_async = bctx.run_cmd_async
        run_download = bctx.run_download
        run_shellscript_async = bctx.run_shellscript_async
        run_light_download = bctx.run_light_download

        tag = self.version_to_tag(version)
        if not repo_path.exists():
            await run_download(run_cmd_async(f'git clone --depth=1 -b {tag} {git_url} {libid}', cwd=repo_path.prnt))
            assert repo_path.exists()
        else:   # fetch version and checkout
            await run_light_download(run_shellscript_async(f'''
git fetch --depth=1 origin +refs/tags/{tag}:refs/tags/{tag}
git checkout tags/{tag}''', cwd=repo_path))



    def _set_config(self, config: InstallConfig):
        if config is not None:
            self.set_config(config)

    def version_to_tag(self, version) -> str:
        return version
