import asyncio
import json
import logging
import importlib

from cbutil import *

import fxpkg
proj_root = Path(__file__).prnt.prnt
root = proj_root/'tmp/v/demo'
fxpkg.init_fxpkg(root)
from fxpkg.all import *



add_package_path(Path(__file__).prnt/'pkgs')
print(import_package('gflags').A)



class CMakePkgMgr:
    def __init__(self, libid, git_url = None):
        if git_url is None:
            git_url = f'https://github.com/{libid}/{libid}.git'
            
        self.libid = libid
        self.git_url = git_url

    def set_config(self, config:InstallConfig):
        self.config = config
        build_type = config.build_type
        version = config.version

        self.repo_path = config.download_path
        self.build_path = (config.build_path/version/build_type).absolute()
        self.install_path = config.install_path/version/build_type

    async def request(self, config:InstallConfig=None):
        self._set_config(config)
        config = self.config
        libid = self.libid
        git_url = self.git_url
        build_type = config.build_type
        version = config.version
        repo_path = self.repo_path
        build_path = self.build_path
        install_path = self.install_path
        
        for p in (build_path, install_path):
            p.mkdir()

        # download
        await self.download()

        # configure
        cmake_presets = make_cmake_presets(config, install_path)
        with (repo_path/'CMakeUserPresets.json').open('w', encoding='utf8') as fw:
            fw.write(json.dumps(cmake_presets, ensure_ascii=False,indent=4))
        assert (repo_path/'CMakeUserPresets.json').exists()
        await run_light_proc(run_cmd_async(f'cmake . -B {build_path} --preset=real', cwd=repo_path))

        # build
        await run_heavy_proc(run_cmd_async(f'cmake --build {build_path}', cwd=repo_path))

        # install
        await run_light_proc(run_cmd_async(f'cmake --build {build_path} --target install --config {build_type}', cwd=repo_path))
        install_entry = InstallEntry()
        install_entry.install_path = install_path
        install_entry.include_path = install_path/'include'
        install_entry.lib_path = install_path/'lib'
        install_entry.cmake_path = install_path/'lib/cmake'
        return install_entry

    async def download(self, config:InstallConfig=None):
        self._set_config(config)
        config = self.config
        libid = self.libid
        git_url = self.git_url
        version = config.version
        repo_path = self.repo_path

        if not repo_path.exists():
            await run_download(run_shellscript_async(f'git clone --depth=1 -b v{version} {git_url} {libid}', cwd = repo_path.prnt))
            assert repo_path.exists()
        else:   # fetch version and checkout
            await run_light_download(run_shellscript_async(f'''
git fetch --depth=1 origin +refs/tags/{version}:refs/tags/{version}
git checkout tags/{version}''', cwd=repo_path))

    def _set_config(self, config:InstallConfig):
        if config is not None:
            self.set_config(config)






cmake_pkg = CMakePkgMgr('gflags')


async def main():
    libid = 'gflags'

    config = InstallConfig()
    config.install_path = path.cache/'install'/libid
    config.download_path = path.cache/'download'/libid
    config.build_path = path.cache/'build'/libid
    config.build_type = 'debug'
    config.version = '2.1.2+'

    msvc_infos = await get_msvc_infos()
    config.toolset.msvc_infos = msvc_infos
    config.cmake.generator = get_cmake_generator(config)

    await cmake_pkg.request(config)
    

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


















