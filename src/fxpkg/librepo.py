import sqlalchemy as sa
from .util import *
from functools import reduce
import pickle

lib_idxs = ['name', 'version', 'pub_date', 'arch', 'platform', 'build_type', 'other_idxs']
lib_basic_idxs = ['name', 'arch', 'platform', 'build_type']
lib_data = ['src_path', 'inc_path', 'lib_path', 'bin_path', 'cmake_path', 'dependency', 'other_data']
lib_fields = lib_idxs+lib_data
lib_trip = ['arch', 'platform', 'build_type']


def bind_lib_table(metadata):
    from sqlalchemy import text
    from sqlalchemy import Table, Column, BLOB
    from sqlalchemy import Integer, String
    from sqlalchemy import PrimaryKeyConstraint

    cols = []
    for field in lib_idxs[0:-1]:
        cols.append(Column(field, String, server_default = ['', None][field in lib_basic_idxs])  )
    cols.append(Column(lib_idxs[-1], BLOB,  server_default =  text("x''")))

    for field in lib_data[0:-2]:
        cols.append(Column(field, String))
    for field in lib_data[-2:]:
        cols.append(Column(field, BLOB))

    pkc = PrimaryKeyConstraint(*lib_idxs)
    tb = Table('lib', metadata,
        *cols,pkc
    )
    return tb

def canonicalize_data(x):
    t = type(x)
    if t in {int,float,str, bytes, bytearray}:
        return x
    return str(x)

class LibRepo:
    def __init__(self, data_path = 'lib_data', debug = False, reinit = False):
        dbname = 'librepo.db'
        dp = Path(data_path) #dp = data_path
        db_path = dp/dbname
        dp.mkdir(overwrite=False)
        if reinit: db_path.remove()
        self.engine = engine = sa.create_engine('sqlite:///' + str(db_path.absolute()), echo = debug)
        self.conn = engine.connect()
        self.data_path = dp
        metadata = sa.MetaData()
        self.table = bind_lib_table(metadata)
        metadata.create_all(engine)

    def update(self, key:dict, value:dict):
        keys = cart_prod_dict(key)
        ncols = []
        for key in keys:
            key.update(value)
            col = key
            nkvs = []
            for k,v in col.items():
                if k == 'dependency':
                    v = pickle.dumps(v)
                else:
                    v = canonicalize_data(v)
                nkvs.append((k,v))
            col = dict(nkvs)
            ncols.append(col)
        cols = ncols  
        conn,table = self.conn,self.table
        conn.execute(table.insert(),*cols)
        
    def find(self, key:dict):
        conn,table = self.conn,self.table
        conds = []
        for k,v in key.items():
            k = getattr(table.c, k)
            if type(v) not in [list,tuple]:
                conds.append(k == v)
            else:
                conds.append(k.in_(v))
        cond = reduce(lambda a,b: a&b, conds)
        print(str(cond))
        ret = conn.execute(sa.select([table]).where(cond))
        return list(ret)
    # def __del__(self):
    #     self.conn.close()

__all__ = ['LibRepo']