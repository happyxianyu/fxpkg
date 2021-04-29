import logging

from fxpkg.db import *
from fxpkg.util.path import Path


print = logging.debug


self_path = Path(__file__)
test_path = self_path.prnt
tmp_path = test_path/'tmp/test_db'


def test_install_info_repo():
    path = tmp_path/'install_info.db'
    path.remove()
    repo = InstallInfoRespository(path, echo = True)
    with repo.db.engine.begin() as conn:
        print(type(conn))