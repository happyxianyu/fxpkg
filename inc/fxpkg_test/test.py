from fxpkg.db import LibDb
from fxpkg.dao import LibInfoDao
from fxpkg import FxpkgHost, init_fxpkg_root, LibConfig
from cbutil import Path

from fxpkg_test.config import *

# init_fxpkg_root(fxpkg_root_path, overwrite=True)
host = FxpkgHost(fxpkg_root_path,debug=True)

config = LibConfig()
host.add_port(port_path/'boost')
host.install('boost', config)
# from dataclasses import dataclass
# from fxpkg.util import DirectDict

