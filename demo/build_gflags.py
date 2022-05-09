import asyncio
from cbutil import *
from fxpkg import *


proj_path = Path(__file__).prnt.prnt
test_path = proj_path/'tmp/v/demo'

add_package_path(Path(__file__).prnt/'pkgs')


async def main():
    libid = 'gflags'
    bctx = await make_build_ctx(test_path)
    pkg_mngr = bctx.get_package_mgr(libid)
    config = bctx.make_config(libid)
    config.version = '2.2.0'
    entry = await pkg_mngr.request(config)
    print(entry)

    

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


















