import typing
if typing.TYPE_CHECKING:
    from fxpkg import *

__all__ = ['PackageMgrBase']

class PackageMgrBase:
    def set_config(self, config:'InstallConfig'):
        pass

    async def request(self, config:'InstallConfig'=None) -> 'InstallEntry':
        pass

    def get_dependency(self, config:'InstallConfig'=None):
        pass



