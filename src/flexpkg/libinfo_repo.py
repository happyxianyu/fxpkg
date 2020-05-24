import sqlalchemy as sa
from util import *
from functools import reduce
import pickle

libinfo_idxs = ['name', 'version', 'pub_date', 'arch', 'platform', 'build_type', 'other_idxs']
libinfo_basic_idxs = ['name', 'arch', 'platform', 'build_type']
libinfo_data = ['src_path', 'inc_path', 'lib_path', 'bin_path', 'cmake_path', 'dependency', 'other_data']
libinfo_fields = libinfo_idxs+libinfo_data
libinfo_trip = ['arch', 'platform', 'build_type']


def bind_libinfo_table(metadata):
    from sqlalchemy import text
    from sqlalchemy import Table, Column, BLOB
    from sqlalchemy import Integer, String
    from sqlalchemy import PrimaryKeyConstraint

    cols = []
    for field in libinfo_idxs[0:-1]:
        cols.append(Column(field, String, server_default = ['', None][field in libinfo_basic_idxs])  )
    cols.append(Column(libinfo_idxs[-1], BLOB,  server_default =  text("x''")))

    for field in libinfo_data[0:-2]:
        cols.append(Column(field, String))
    for field in libinfo_data[-2:]:
        cols.append(Column(field, BLOB))

    pkc = PrimaryKeyConstraint(*libinfo_idxs)
    tb = Table('LibInfo', metadata,
        *cols,pkc
    )
    return tb

def canonicalize_data(x):
    t = type(x)
    if t in {int,float,str, bytes, bytearray}:
        return x
    return str(x)

class LibInfoRepo:
    def __init__(self, data_dir = 'libinfo_data', debug = False, reinit = False):
        dp = Path(data_dir) #dp = data_path
        if reinit: dp.remove()
        dp.safe_mkdir()
        db_path = dp/'libinfo.db'
        self.engine = engine = sa.create_engine('sqlite:///' + str(db_path.absolute()), echo = debug)
        self.conn = engine.connect()
        self.data_path = dp
        metadata = sa.MetaData()
        self.table = bind_libinfo_table(metadata)
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
