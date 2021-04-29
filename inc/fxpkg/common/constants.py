import enum
from enum import Enum


InstallState = Enum('InstallState', 
'''
    INTACT
    DAMAGE
    INSTALLING
    UNINSTALLING
    FAIL_INSTALLI
    FAIL_UNINSTALL
''')




del Enum
del enum