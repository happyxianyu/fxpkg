from sqlalchemy import Column, Integer, String, BLOB, Integer, UniqueConstraint
from sqlalchemy import TypeDecorator

import pickle

from fxpkg.db.globalval import Base
from fxpkg.util.sa import get_tbcls_col_names
from fxpkg.util import Path

class PyObjSaType(TypeDecorator):
    impl = BLOB

    def process_bind_param(self, value, dialect):
        if value != None:
            return pickle.dumps(value)
 
    def process_result_value(self, value, dialect):
        if value != None:
            return pickle.loads(value)

class PathSaType(TypeDecorator):
    impl = String

    def process_bind_param(self, value:Path, dialect):
        if value != None:
            return str(value)
 
    def process_result_value(self, value:str, dialect):
        if value != None:
            return Path(value)


class LibInfo(Base):
    __tablename__='LibInfo'

    id = Column(Integer, primary_key= True, autoincrement = True)

    name = Column(String, nullable = False, index=True)
    version = Column(String, nullable = False)

    platform = Column(String, server_default="")
    arch = Column(String, server_default="")
    build_type = Column(String, server_default="")

    #If path is relative, it is relative to the path the fxpkg host root directory
    #Any paths in the fxpkg root dir should be stored relatively
    install_path = Column(PathSaType) #use for uninstalling
    inc_path = Column(PathSaType)
    lib_path = Column(PathSaType)
    bin_path = Column(PathSaType)
    cmake_path = Column(PathSaType)

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

    def set_paths_absolute(self):
        for a in self.path_col_names:
            v:Path = getattr(self, a)
            if v != None:
                if not v.is_absolute():
                    setattr(self, a, v.absolute())
    
    def set_paths_relative(self, base_path:Path):
        for a in self.path_col_names:
            v:Path = getattr(self, a)
            if v != None:
                if not v.is_absolute():
                    setattr(self, a, v.relative_to(base_path))
    
    def make_eq_expr_list(self, apply_col_names:list = None):
        ret = []
        if apply_col_names is None:
            apply_col_names = self.col_names
        for a in apply_col_names:
            v = getattr(self, a, default= None)
            if v != None:
                ret.append(getattr(LibInfo,a)== v)
        return ret

    def make_query(self, sess, apply_col_names:list = None):
        return self.sess.query(LibInfo).filter(*self.make_eq_expr_list(apply_col_names))

    def make_key_dict(self, sub_None = False):
        if sub_None:
            d = {k:getattr(self,k) for k in ['name', 'version']}
            for a in ['platform', 'arch', 'build_type']:
                v = getattr(self, a)
                if v is None:
                    v = ''
                d[a] = v
            return d 
        else:
            return {k:getattr(self, k) for k in self.key_col_names}

LibInfo.col_names = get_tbcls_col_names(LibInfo)
LibInfo.path_col_names = ['install_path', 'inc_path', 'lib_path', 'bin_path', 'cmake_path']
LibInfo.key_col_names = ['name', 'version', 'platform', 'arch', 'build_type']

__all__ = ['LibInfo']