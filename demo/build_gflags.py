import asyncio
from cbutil import *
from fxpkg import *


proj_path = Path(__file__).prnt.prnt
test_path = proj_path/'tmp/v/demo'

add_package_path(Path(__file__).prnt/'pkgs')
print(import_package('gflags').A)




async def main():
    libid = 'gflags'
    bctx = await make_build_ctx(test_path)
    cmake_pkg = CMakePkgMgr(bctx, 'gflags')
    config = bctx.make_config(libid)
    config.version = '2.2.1'
    await cmake_pkg.request(config)

    

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


















