from .path import Path

def get_tbcls_col_names(tbcls):
    tb = tbcls.__table__
    return [c.key for c in tb.c]

def path_to_sqlite_url(p: Path):
    p = str(p)
    p = p.replace('\\', '/')
    return 'sqlite:///' + p