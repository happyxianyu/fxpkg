import logging
import asyncio
from dataclasses import dataclass

from cbutil import CoroExecutor
from rmgr.all import path


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .common import InstallConfig


__all__ = ['bctx', 'log', 'path', 'run_download', 'run_light_download','run_light_proc', 'run_heavy_proc']


log = logging

@dataclass
class _Path(type(path)):
    installed = path.cache/'installed'
    config = path.data/'config'

path = _Path()




class BuildExecutor:
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


class BuildContext(BuildExecutor):
    def __init__(self):
        super().__init__()



global run_download
global run_light_download
global run_light_proc
global run_heavy_proc


install_config_template:'InstallConfig'

bctx:BuildContext



def _ainit1():
    global run_download
    global run_light_download
    global run_light_proc
    global run_heavy_proc
    global bctx
    bctx = BuildContext()
    build_exec = BuildExecutor()
    run_download = build_exec.run_download
    run_light_download = build_exec.run_light_download
    run_light_proc = build_exec.run_light_proc
    run_heavy_proc =build_exec.run_heavy_proc 


async def ainit():
    _ainit1()
    # import fxpkg.helpler    # to initialize install_config_template

# def init():
loop = asyncio.get_event_loop()
loop.run_until_complete(ainit())






