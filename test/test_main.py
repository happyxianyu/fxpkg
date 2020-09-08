import logging
from random import randint

from fxpkg.fxhost import FxHostDir, FxHost
from fxpkg.model import LibInfo

from .info import *


log = logging.getLogger(__name__)

fxpkg_root = PathInfo.test_cache/'fxpkg-root'

def make_rand_libinfo():
    def randstr():
        return str(randint(0, 1<<64))
    return LibInfo(**{k:randstr() for k in LibInfo.col_names})

def test_HostDir():
    root = fxpkg_root
    host_dir = FxHostDir(root)
    host_dir.recreate()
    for attr in host_dir.attrs:
        log.info(f'{attr}: ' + getattr(host_dir, attr).str)
    info = host_dir.make_libpathinfo('LibName')
    log.info(info)
    log.info(info.make_sub_info('0.0'))

def test_fxhost():
    port_name = 'port1'
    host = FxHost(fxpkg_root)
    host.add_port(PathInfo.test_port/f'{port_name}.py')
    port = host.make_port(port_name)
    port.host
    log.info(port.lib_path_info)

def test_db():
    host = FxHost(fxpkg_root, debug = True, reinit=True)
    db = host.db
    service = host.libservice

    info = make_rand_libinfo()
    log.info(info)
    service.store_libinfo(info, 7)
    info1 = service.get_libinfo(**info.make_key_dict(sub_None=True))

        