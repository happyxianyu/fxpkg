import typing
import logging
import dataclasses
from dataclasses import dataclass
import asyncio
from copy import deepcopy

from rmgr import *
from cbutil import CoroExecutor, Path

from fxpkg.helpler import *
from fxpkg.common import *
from .core import *
if typing.TYPE_CHECKING:
    from .pkgbase.base import PackageMgrBase

__all__ = ['BuildContext', 'make_build_ctx']


class BuildExecutor:
    """
    must use it in coroutine
    """
    def __init__(self):
        self.donwload_executor = CoroExecutor(3)
        self.light_download_executor = CoroExecutor(16)
        self.heavy_proc_executor = CoroExecutor(1)
        self.light_proc_executor = CoroExecutor(8)

    def run_light_download(self, coro) -> asyncio.Future:
        return self.light_download_executor.submit_nw(coro)

    def run_download(self, coro) -> asyncio.Future:
        return self.donwload_executor.submit_nw(coro)

    def run_light_proc(self, coro) -> asyncio.Future:
        return self.light_proc_executor.submit_nw(coro)

    def run_heavy_proc(self, coro) -> asyncio.Future:
        return self.heavy_proc_executor.submit_nw(coro)


@dataclass 
class PathInfoEx(PathInfo):
    build:Path = None
    download:Path = None
    install:Path = None
    config:Path = None
    package:Path = None



class BuildContext(BuildExecutor, ResContext):
    def __init__(self, root:Path, _direct_call=True):
        self.log = log = logging
        if _direct_call:
            raise Exception('Do not call it directly, use make_build_ctx instead')

        ResContext.__init__(self, root)
        BuildExecutor.__init__(self)
        path = self.path
        self.path = path = PathInfoEx(
            build = path.cache/'build',
            download = path.cache/'download',
            install = path.cache/'install',
            config = path.data/'config',
            package = path.data/'package',
            **dataclasses.asdict(path)
        )
        path.create_path()

        add_package_path(path.package)
        self._tpl_install_config:InstallConfig = None   # template install config

    def make_config(self, libid:str):
        path = self.path
        config = deepcopy(self._tpl_install_config)
        config.install_path = path.install/libid
        config.download_path = path.download/libid
        config.build_path = path.build/libid
        config.install_path.mkdir()
        config.build_path.mkdir()
        config.build_path.mkdir()
        config.build_type = 'debug'
        config.version = '2.2.2'
        config.cmake.generator = get_cmake_generator(config)
        return config

    def get_package_mgr(self, libid:str) -> 'PackageMgrBase':
        return get_package_mgr(self, libid)

    def add_package_mgr(self, mgr_path):
        path = self.path
        mgr_path = Path(mgr_path)
        mgr_path.copy_to(path.package, is_prefix=True)




async def make_build_ctx(root:Path):
    bctx = BuildContext(root, _direct_call= False)
    config = InstallConfig()
    config.toolset.msvc_infos = await get_msvc_infos(bctx)
    bctx._tpl_install_config = config
    return bctx



