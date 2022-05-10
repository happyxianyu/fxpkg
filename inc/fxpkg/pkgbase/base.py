import typing
from fxpkg import InstallConfig, InstallEntry, BuildContext

__all__ = ['PackageMgrBase']

class PackageMgrBase:
    def set_config(self, config:'InstallConfig'):
        raise NotImplementedError

    async def request(self, config:'InstallConfig'=None) -> 'InstallEntry':
        raise NotImplementedError

    def get_dependency(self, config:'InstallConfig'=None):
        raise NotImplementedError




