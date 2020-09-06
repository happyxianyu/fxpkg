from sqlalchemy import Column, String, BLOB, Integer

from fxpkg.db.globalval import Base
from fxpkg.util.sa import get_tbcls_col_names

class LibInfo(Base):
    __tablename__='LibInfo'

    name = Column(String, primary_key=True, nullable = False, index=True)
    version = Column(String, primary_key=True, nullable = False)

    platform = Column(String, primary_key=True, server_default="")
    arch = Column(String, primary_key=True, server_default="")
    build_type = Column(String, primary_key=True, server_default="")

    inc_path = Column(String)
    lib_path = Column(String)
    bin_path = Column(String)
    cmake_path = Column(String)

    dependency = Column(BLOB)   
    dependent = Column(BLOB)

    def to_str(self, ts = str):
        l = []
        for k in LibInfo.col_names:
            v = getattr(self, k)
            l.append(f'{ts(k)}: {ts(v)};')
        return self.__tablename__+'{' + ''.join(l) + '}'
        
    def __repr__(self):
        return self.to_str(repr)

    def __str__(self):
        return self.to_str(str)

LibInfo.col_names = get_tbcls_col_names(LibInfo)

__all__ = ['LibInfo']