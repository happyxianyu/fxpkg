import sqlalchemy as sa
from sqlalchemy.engine import Connection
from fxpkg.model.globalval import metadata

class MainDb:
    def __init__(self, url:str = 'sqlite:///:memory:', echo = False):
        self.engine = engine = sa.create_engine(url, echo = echo)
        self.conn = conn = engine.connect()
        self.exec = conn.execute
        self.create_all()

    def create_all(self):
        engine = self.engine
        metadata.create_all(engine)

    def drop_all(self):
        engine = self.engine
        metadata.drop_all(engine)

__all__ = ['MainDb']