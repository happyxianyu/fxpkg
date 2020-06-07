import sys
from fxpkg import *
from fxpkg.util import Path

self_path = Path(__file__)
root_path = self_path.prnt
host = FxpkgHost(root_path)