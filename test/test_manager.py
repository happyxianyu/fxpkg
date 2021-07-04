import logging
import pytest

from fxpkg import *
import asyncio

print = logging.debug

self_path = Path(__file__)
prnt_path = self_path.prnt
test_path = prnt_path/'tmp/test_host'
resource_path = prnt_path/'resource'
pkg_path = resource_path/'package'


def test_lib_manager_pkg():
    async def impl():
        pkg_name = 'fmt'
        host = Host(test_path / 'fxpkg')
        manager = host.libManager
        manager.add_package(pkg_path/f'{pkg_name}.py')
        pkg = manager.get_package('fmt')
        assert pkg.libManager is manager
        config = InstallConfig()
    asyncio.run(impl())


def test_lib_manager_install():
    async def impl():
        pkg_name = 'fmt'
        host = Host(test_path / 'fxpkg')
        manager = host.libManager
        manager.add_package(pkg_path / f'{pkg_name}.py')
        config = InstallConfig()
        config.libid = pkg_name
        await manager.install_lib(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(impl())