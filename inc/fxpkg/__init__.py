import logging

import fxpkg.package
_tmp = fxpkg.package

from .util import *
from .core import *
fxpkg.package = _tmp    #fixme: fxpkg.package 会变为 fxpkg.core.package
from .common import *
import fxpkg.interface

fxpkg.package = _tmp