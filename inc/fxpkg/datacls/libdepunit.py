from dataclasses import dataclass

from fxpkg.util import VersionInterval

@dataclass
class LibDepUnit:
    name:str
    ver_interval:VersionInterval = VersionInterval()