import asyncio
import sys

from cbutil import *
from fxpkg import *


argv = sys.argv
if(len(argv)<2):
    exit(0)

libid = argv[1]


async def main():
    root = Path(__file__).prnt
    bctx = await make_build_ctx(root)
    mgr = bctx.get_package_mgr(libid)
    config = bctx.make_config(libid)
    entry = await mgr.request(config)
    bctx.log.info(entry)

    

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


