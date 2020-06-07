from cbutil import Path
tmp_path = Path(r'D:\temp')
import sys
sys.path.insert(0,Path.getcwd())

from fxpkg import init_fxpkg_root
from fxpkg import FxpkgHost
import importlib

root = init_fxpkg_root(tmp_path,is_prefix=True, overwrite=True)
host = FxpkgHost(root)
print(host.port.__path__)
host.get_port('boost')

