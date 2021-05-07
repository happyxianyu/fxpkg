import sqlite3

import plyvel
import sqlalchemy as sa


class SqliteDb:
    def __init__(self, url=':memory:'):
        self.con = sqlite3.connect(url)
        self.cur = self.con.cursor()

    def commit(self):
        self.con.commit()

    def close(self):
        self.con.close()


class SaDb:
    def __init__(self, url='sqlite:///:memory:', echo=True):
        self.engine = sa.create_engine(url, echo=echo)
        self.metadata = self.make_metadata()
        self.conn = self.connect()

    def make_metadata(self):
        return sa.MetaData(bind=self.engine)

    def connect(self) -> sa.engine.Connection:
        return self.engine.connect()

    def create_tables(self):
        self.metadata.create_all()

    def close(self):
        self.conn.close()


class LevelDb:
    def __init__(self, path):
        self.db = plyvel.DB(str(path), create_if_missing=True)

    def put(self, k: bytes, v: bytes = b''):
        self.db.put(k, v)

    def puts(self, k: str, v: str):
        self.db.put(k.encode('utf-8'), v.encode('utf-8'))

    def get(self, k: bytes, default=None) -> bytes:
        return self.db.get(k, default)

    def gets(self, k: str, default=None) -> str:
        result: bytes = self.db.get(k.encode('utf-8'), default)
        if result is default:
            return default
        return result.decode('utf-8')

    def delete(self, k: bytes):
        self.db.delete(k)

    def deletes(self, k: str):
        k = k.encode('utf-8')
        self.db.delete(k)

    def write_batch(self):
        return self.db.write_batch()

    def snapshot(self):
        return self.db.snapshot()

    def __iter__(self):
        return iter(self.db)

    def close(self):
        self.db.close()
