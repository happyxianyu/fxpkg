import sqlalchemy as sa
from sqlalchemy import Column, String, BLOB, Integer

from .globalval import Base

LibInfo_field_key = ['name', 'version', 'arch', 'build_type', 'platform']
LibInfo_field_val = ['src_path', 'inc_path', 'lib_path', 'bin_path', 'cmake_path', 'dependency']
LibInfo_field_all = LibInfo_field_key + LibInfo_field_val

class LibInfo(Base):
    __tablename__='LibInfo'

    #primary key
    name = Column(String, primary_key=True, nullable = False, index=True)
    version = Column(String, primary_key=True, server_default="")
    arch = Column(String, primary_key=True, nullable = False)
    build_type = Column(String, primary_key=True, nullable = False)
    platform = Column(String, primary_key=True, server_default="")

    #path   
    src_path = Column(String)
    inc_path = Column(String)
    lib_path = Column(String)
    bin_path = Column(String)
    cmake_path = Column(String)

    dependency = Column(BLOB)   
    depended = Column(BLOB)


    @staticmethod
    def cvt_obj_to_dict(o:object) -> dict:
        item = {}
        for name in LibInfo_field_all:
            if hasattr(o, name):
                if val := getattr(o, name):
                    item[name] = val
        return item

__all__ = ['LibInfo', 'LibInfo_field_key', 'LibInfo_field_val', 'LibInfo_field_all']