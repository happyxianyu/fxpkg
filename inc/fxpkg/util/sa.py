from contextlib import contextmanager

from .path import Path

__all__ = []

def allf(f):
    __all__.append(f.__name__)
    return f

@allf
def get_tbcls_col_names(tbcls):
    tb = tbcls.__table__
    return [c.key for c in tb.c]

@allf
def path_to_sqlite_url(p: Path):
    p = str(p)
    p = p.replace('\\', '/')
    return 'sqlite:///' + p

@allf
@contextmanager
def with_sess(sess):
    try:
        yield sess
        sess.commit()
    except:
        sess.rollback()
