import asyncio

from rmgr import *


def init_fxpkg(root:Path):
    init_rmgr(root)
    import fxpkg.config as config # ensure config be initialized firstly
    loop = asyncio.get_event_loop()
    loop.run_until_complete(config.ainit())

    