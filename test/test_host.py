import logging

from fxpkg import *

print = logging.debug

self_path = Path(__file__)
prnt_path = self_path.prnt
test_path = prnt_path/'tmp/test_host'

def test_host():
    host = Host(test_path/'fxpkg')