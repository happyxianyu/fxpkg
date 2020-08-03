from fxpkg.fxhost import FxpkgHostPathConfig
from fxpkg_test.config import *

path_config = FxpkgHostPathConfig(fxpkg_root_path)
path_config.create_path()
print(path_config)