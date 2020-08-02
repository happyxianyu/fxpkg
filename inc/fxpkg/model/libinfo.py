import sqlalchemy as sa
from sqlalchemy import Column, String, BLOB, Integer

from .globalval import Base


class LibInfo(Base):
    __tablename__='LibInfo'

    #primary key
    name = Column(String, primary_key=True, nullable = False, index=True)
    arch = Column(String, primary_key=True, nullable = False)
    build_type = Column(String, primary_key=True, nullable = False)
    platform = Column(String, primary_key=True, server_default="")
    version = Column(String, primary_key=True, server_default="")
    
    #path
    src_path = Column(String)
    inc_path = Column(String)
    lib_path = Column(String)
    bin_path = Column(String)
    cmake_path = Column(String)

    dependency = Column(BLOB)

__all__ = ['LibInfo']