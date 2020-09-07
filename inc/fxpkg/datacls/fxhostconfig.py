from dataclasses import dataclass
import platform

from .libtriplet import LibTriplet

if platform.architecture()[0].find('64')>=0:
    arch = 'x64'
else:
    arch = 'x86'

class FxHostConfig:
    libtriplet:LibTriplet = LibTriplet(platform=platform.platform().lower(), arch = 'x64', build_type='debug')

__all__ = ['FxHostConfig']