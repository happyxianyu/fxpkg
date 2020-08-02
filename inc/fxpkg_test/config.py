from cbutil import Path
from more_itertools import nth

self_path = Path(__file__)
cache_path = self_path.prnt/'test_cache'
project_path = nth(self_path.parents,2)
fxpkg_root_path = cache_path/'fxpkg_root'
port_path = project_path/'port'