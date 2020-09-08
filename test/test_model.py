from fxpkg.model import LibInfo

import logging

log = logging.getLogger(__name__)


def test_libinfo():
    info = LibInfo(name = 'name')
    log.info(info)