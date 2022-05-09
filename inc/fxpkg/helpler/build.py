import platform
from .msvc import *
from .cmake import *

def get_sys_info():
    '''
    返回(platform, arch)
    '''
    uname = platform.uname()
    return uname.system.lower(), uname.machine.lower()
    




