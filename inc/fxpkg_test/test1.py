from fxpkg.dao.libinfodao import *
from fxpkg.db import MainDb

db = MainDb(echo=True)
dao = LibInfoDao(db.exec)

v = {
    'name' : 'abc',
    'version' : '2342',
    'arch' : 'arch',
    'build_type' : 'build_type',
    'platform' : 'windows',
    # 'src_path' : 'root/path'
}

dao.add(v)
dao.add(v)

ret = dao.get_all()

print(list(ret))