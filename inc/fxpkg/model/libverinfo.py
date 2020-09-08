from sqlalchemy import Column, Integer, String

from fxpkg.db.globalval import Base
from fxpkg.util.sa import get_tbcls_col_names


class LibVerInfo(Base):
    __tablename__ = 'LibVerInfo'
    name = Column(String, nullable = False, primary_key = True)
    version = Column(String, nullable = False, primary_key = True)

    mask = Column(Integer, server_default = '7')

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

    @staticmethod
    def make_by_libinfo(libinfo, mask) -> 'LibVerInfo':
        return LibVerInfo(name = libinfo.name, version = libinfo.version, mask = mask)
        

LibVerInfo.col_names = get_tbcls_col_names(LibVerInfo)

__all__ = ['LibVerInfo']