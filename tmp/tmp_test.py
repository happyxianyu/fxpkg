import sqlite3
import mimesis
from random import randint

from fxpkg.util import Path

from fxpkg.core import Host, setup_fxpkg

test_dir = Path(__file__).prnt
tmp_dir = test_dir/'tmp'
tmp_dir.mkdir()

resource_dir = test_dir/'resource'
test_package_dir = resource_dir/'package'
testpkg_path = test_package_dir/'testpkg.py'

root_path = tmp_dir
host = setup_fxpkg(root_path)
libManager = host.libManager
libManager.add_package(testpkg_path)
pkg = libManager.get_package('testpkg')

