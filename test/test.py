# from fxpkg.db import LibDb
# from fxpkg.dao import LibInfoDao
# from fxpkg import FxpkgHost, init_fxpkg_root
# from cbutil import Path

# self_path = Path(__file__)
# cache_path = self_path.prnt/'test_cache'

# root_path = init_fxpkg_root(cache_path/'root', overwrite=True)
# host = FxpkgHost(root_path,debug=True)


from dataclasses import dataclass
from fxpkg.util import DirectDict


@dataclass
class A(DirectDict):
    a:int = 1
    b:str = '4342'



v = A(1,'324')
print(dir(A))

print(v)
print('_data' in dir(v))