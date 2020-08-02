def path_to_sqlite_url(p):
    p = str(p)
    p = p.replace('\\', '/')
    return 'sqlite:///' + p