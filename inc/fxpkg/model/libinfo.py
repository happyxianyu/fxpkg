from sqlalchemy import Column, Integer, String, BLOB, Integer, UniqueConstraint
from sqlalchemy import TypeDecorator

import pickle

from fxpkg.db.globalval import Base
from fxpkg.util.sa import get_tbcls_col_names

class PyObjSaType(TypeDecorator):
    impl = BLOB

    def process_bind_param(self, value, dialect):
        return pickle.dumps(value)
 
    def process_result_value(self, value, dialect):
        return pickle.loads(value)


class LibInfo(Base):
    __tablename__='LibInfo'

    id = Column(Integer, primary_key= True, autoincrement = True)

    name = Column(String, nullable = False, index=True)
    version = Column(String, nullable = False)

    platform = Column(String, server_default="")
    arch = Column(String, server_default="")
    build_type = Column(String, server_default="")

    install_path = Column(String) #use for uninstalling
    inc_path = Column(String)
    lib_path = Column(String)
    bin_path = Column(String)
    cmake_path = Column(String)

    dependency = Column(PyObjSaType)   
    dependent = Column(PyObjSaType)

    UniqueConstraint(name, version, platform, arch, build_type)

    def to_str(self, ts = str):
        l = []
        for k in self.col_names:
            v = getattr(self, k)
            l.append(f'{ts(k)}: {ts(v)};')
        return self.__tablename__+'{' + ''.join(l) + '}'
        
    def __repr__(self):
        return self.to_str(repr)

    def __str__(self):
        return self.to_str(str)

LibInfo.col_names = get_tbcls_col_names(LibInfo)

__all__ = ['LibInfo']