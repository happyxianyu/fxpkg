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

cmake_pkg = CMakePkgMgr('gflags')


async def main():
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


















