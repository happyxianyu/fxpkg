import asyncio
import json
import logging
from cbutil import *

from fxpkg import *
proj_root = Path(__file__).prnt.prnt
root = proj_root/'tmp/v/demo'
init_fxpkg(root)
from fxpkg.all import *


class BuildExecutor:
    def __init__(self):
        self.donwload_executor = CoroExecutor()
        self.heavy_proc_executor = CoroExecutor(1)
        self.light_proc_executor = CoroExecutor(10)


    def run_download(self, coro) -> asyncio.Future:
        return self.donwload_executor.submit_nw(coro)

    def run_light_proc(self, coro) -> asyncio.Future:
        return self.light_proc_executor.submit_nw(coro)

    def run_heavy_proc(self, coro) -> asyncio.Future:
        return self.heavy_proc_executor.submit_nw(coro)

global run_download
global run_light_proc
global run_heavy_proc



class CMakePkgMgr:
    def __init__(self, libid, git_url = None):
        if git_url is None:
            git_url = f'https://github.com/{libid}/{libid}.git'
            
        self.libid = libid
        self.git_url = git_url

    async def request(self, config:InstallConfig):
        libid = self.libid
        git_url = self.git_url
        build_type = config.build_type
        version = config.version

        repo_path = config.download_path
        build_path = (config.build_path/version/build_type).absolute()
        install_path = config.install_path/version/build_type
        
        for p in (build_path, install_path):
            p.mkdir()

        if not repo_path.exists():
            await run_download(run_shellscript_async(f'git clone --depth=1 -b v{version} {git_url} {libid}', cwd = repo_path.prnt))
            assert repo_path.exists()
        else:   # fetch version and checkout
            await run_shellscript_async(f'''
git fetch --depth=1 origin +refs/tags/{version}:refs/tags/{version}
git checkout tags/{version}''', cwd=repo_path)
        cmake_presets = make_cmake_presets(config, install_path)
        with (repo_path/'CMakeUserPresets.json').open('w', encoding='utf8') as fw:
            fw.write(json.dumps(cmake_presets, ensure_ascii=False,indent=4))
        assert (repo_path/'CMakeUserPresets.json').exists()
        await run_light_proc(run_cmd_async(f'cmake . -B {build_path} --preset=real', cwd=repo_path))
        assert build_path.exists()
        await run_heavy_proc(run_cmd_async(f'cmake --build {build_path}', cwd=repo_path))
        await run_light_proc(run_cmd_async(f'cmake --build {build_path} --target install --config {config.build_type}', cwd=repo_path))
        installEntry = InstallEntry()
        installEntry.install_path = install_path
        installEntry.include_path = install_path/'include'
        installEntry.lib_path = install_path/'lib'
        installEntry.cmake_path = install_path/'lib/cmake'
        return installEntry



cmake_pkg = CMakePkgMgr('gflags')


async def main():
    global run_download
    global run_light_proc
    global run_heavy_proc
    build_exec = BuildExecutor()
    run_download = build_exec.run_download
    run_light_proc = build_exec.run_light_proc
    run_heavy_proc =build_exec.run_heavy_proc
    libid = 'gflags'

    config = InstallConfig()
    config.install_path = path.cache/'install'/libid
    config.download_path = path.cache/'download'/libid
    config.build_path = path.cache/'build'/libid
    config.build_type = 'debug'
    config.version = '2.2.2'

    msvc_infos = await get_msvc_infos()
    config.toolset.msvc_infos = msvc_infos
    config.cmake.generator = get_cmake_generator(config)

    await cmake_pkg.request(config)
    

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


















