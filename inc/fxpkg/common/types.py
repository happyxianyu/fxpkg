import typing

__all__ = [
    'VersionSetBase'
]
class VersionSetBase:
    def __contains__(self, ver):
        return False

    def __iter__(self) -> typing.Iterable[str]:
        '''
        返回可用版本，不一定要全面
        '''
        return iter([''])


