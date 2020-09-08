from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker, Session

from .globalval import metadata

@contextmanager
def with_sess_impl(db):
    sess:Session = db.sess
    try:
        yield sess
        sess.commit()
    except:
        sess.rollback()
    

class LibDb:
    def __init__(self, url:str = 'sqlite:///:memory:', echo = False):
        self.engine = engine = create_engine(url, echo = echo)
        self.conn = conn = engine.connect()
        Session = sessionmaker(bind=engine)
        self.sess = Session(bind=conn)
        self.create_all()

    def create_all(self):
        engine = self.engine
        metadata.create_all(engine)

    def drop_all(self):
        engine = self.engine
        metadata.drop_all(engine)

    def with_sess(self):
        return with_sess_impl(self)

    

__all__ = ['LibDb']