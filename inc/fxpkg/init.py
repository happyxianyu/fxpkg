from rmgr import *

def init_fxpkg(root:Path):
    init_rmgr(root)
    import fxpkg.config # ensure config be initialized firstly

    