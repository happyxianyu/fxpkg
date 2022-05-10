import typing
from packaging.version import Version, SpecifierSet
from pyinter.interval import closed, IntervalSet

__all__ = [
    'Version',
    'VersionSetBase',
    'VersionSet',
    'closed'
]


class VersionSetBase:
    def __contains__(self, ver):
        return False

    def __iter__(self) -> typing.Iterable[str]:
        '''
        返回候选版本
        '''
        return iter([''])


class VersionSet(IntervalSet):
    def __init__(self, versions):
        super().__init__(versions)

    @staticmethod
    def parse_intervals(s: str) -> VersionSetBase:
        pass




