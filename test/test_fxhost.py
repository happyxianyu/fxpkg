import logging

from fxpkg.fxhost import FxHostDir, FxHost

from .info import *


log = logging.getLogger(__name__)

fxpkg_root = PathInfo.test_cache/'fxpkg-root'

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
