import enum
from enum import Enum, auto


class InstallState(Enum):
    INTACT = auto()
    DAMAGE = auto()
    INSTALLING = auto()
    UNINSTALLING = auto()
    FAIL_INSTALL = auto()
    FAIL_UNINSTALL = auto()
    REF = auto()    # 表示引用路径，卸载时无需删除任何文件


del Enum
del enum
del auto
