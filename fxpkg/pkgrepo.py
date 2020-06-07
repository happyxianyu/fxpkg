import sqlalchemy as sa

from .path import Path
from .libtable import LibTable

class PkgRepo:
    def __init__(self, data_path = 'data', debug = False, reinit = False):
        self.data_path = data_path = Path(data_path)
        data_path.mkdir(overwrite=False)
        if reinit:
            data_path.remove_sons()
        db_path = data_path/'main.db'
        self.engine = engine = sa.create_engine('sqlite:///' + db_path.to_str(), echo = debug)
        self.conn = conn = engine.connect()
        self.data_path = data_path
        self.libtable = LibTable(engine, conn)