import enum
from enum import Enum, auto

__all__ = ['InstallState']

class InstallState(Enum):
    INTACT = auto()
    DAMAGE = auto()
    INSTALLING = auto()
    UNINSTALLING = auto()
    FAIL_INSTALL = auto()
    FAIL_UNINSTALL = auto()



