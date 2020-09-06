from fxpkg.util import Path

class PathInfo:
    test_root = Path(__file__).resolve().prnt
    test_result = test_root/'result'
    test_port = test_root/'port'
    test_cache = test_result/'cache'
    test_log = test_result/'log'

__all__ = ['PathInfo']