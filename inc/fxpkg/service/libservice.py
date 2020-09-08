from sqlalchemy.orm import Session

from fxpkg.model import LibInfo, LibVerInfo
from fxpkg.datacls import LibInfoKey
from fxpkg.util import with_sess

class LibService:
    def __init__(self, sess:Session):
        self.sess = sess
    
    def store_libinfo(self, libinfo:LibInfo, mask:int):
        sess = self.sess
        info_exsited = self.get_libinfo(**libinfo.make_key_dict(sub_None=True))
        if info_exsited is None:
            verinfo = LibVerInfo.make_by_libinfo(libinfo, mask)
            with with_sess(sess):
                sess.add(libinfo)
                sess.merge(verinfo)
        else:
            pass#TODO

    def get_libinfo(self, **kwargs) -> LibInfo:
        return self.sess.query(LibInfo).filter_by(**kwargs).one()

    def find_libinfo(self, **kwargs):
        return self.sess.query(LibInfo).filter_by(**kwargs).all()

    def find_libinfo_by_model(self, libinfo:LibInfo, key_cols_only = False)->list:
        if key_cols_only:
            return libinfo.make_query(libinfo.key_col_names).all()
        else:
            return libinfo.make_query().all()

    def get_libinfo_by_key(self, key:LibInfoKey) -> LibInfo:
        assert(key.platform != None and key.arch != None)
        return self.sess.query(LibInfo).filter_by(**key.to_dict()).one()


__all__ = ['LibService']