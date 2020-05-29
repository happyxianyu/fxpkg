import sys
from cbutil import Path
self_path = Path(sys.path[0] )
sys.path.insert(1, self_path.prnt.to_str())
from fxpkg import *
