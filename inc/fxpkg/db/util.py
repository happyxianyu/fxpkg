import sqlite3
import sqlalchemy as sa

class SqliteDb:
    def __init__(self, url = ':memory:'):
        self.con = sqlite3.connect(url)
        self.cur = self.con.cursor()
    
    def commit(self):
        self.con.commit()

    def close(self):
        self.con.close()

    
class SaDb:
    def __init__(self, url = 'sqlite:///:memory:', echo = True):
        self.engine = sa.create_engine(url, echo = echo)
        self.metadata = self.make_metadata()
        
    def make_metadata(self):
        return sa.MetaData(bind = self.engine)

    def connect(self)  -> sa.engine.Connection:
        return self.engine.connect()


