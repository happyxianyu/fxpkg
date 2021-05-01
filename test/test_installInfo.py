import logging

from fxpkg.db import *
from fxpkg.util.path import Path

print = logging.debug

self_path = Path(__file__)
test_path = self_path.prnt
tmp_path = test_path / 'tmp/test_db'



def test_install_info_respository():
    try:
        path = tmp_path / 'install_info.db'
        path.remove()
        repo = InstallInfoRespository(path, echo=True)
        with repo.db.engine.begin() as conn:
            print(type(conn))
    except:
        assert False


def test_get_by_id():
    try:
        path = tmp_path / 'install_info.db'
        repo = InstallInfoRespository(path, echo=True)
        tb = repo.installEntry_tb
        res = tb.get_by_entry_id(0)
        print(f'res: {res}')
    except:
        assert False