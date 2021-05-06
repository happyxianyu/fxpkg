import enum
from enum import Enum, auto


class InstallState(Enum):
    INTACT = auto()
    DAMAGE = auto()
    INSTALLING = auto()
    UNINSTALLING = auto()
    FAIL_INSTALL = auto()
    FAIL_UNINSTALL = auto()


del Enum
del enum
del auto
