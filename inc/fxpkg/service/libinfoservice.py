from fxpkg.dao import LibInfoDao
from fxpkg.db import MainDbb
from fxpkg.datacls import LibConfig
from fxpkg.model.libinfo import *

class LibInfoService:
    def __init__(self, db:MainDbb):
        self.dao = LibInfoDao(db.exec)

    def store_libinfo_by_object(self, o:object):
        dao = self.dao
        item = LibInfo.cvt_obj_to_dict(o)
        dao.add(item)

    
        

__all__ = ['LibInfoService']