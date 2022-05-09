import logging
from dataclasses import dataclass

from rmgr.all import *

__all__ = ['log', 'path']


log = logging

@dataclass
class _Path(type(path)):
    installed = path.cache/'installed'
    config = path.data/'config'

path = _Path()







