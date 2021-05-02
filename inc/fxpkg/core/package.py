# -*- coding:utf-8 -*-
from fxpkg.common.dataclass import InstallConfig
from .host import Host
from fxpkg.common.types import VersionSetBase
from fxpkg.common.dataclass import *

class InstallerBase:
    def __init__(self, libManager : 'LibManager'):
        self.libManager = libManager

    async def install(self, config: InstallConfig, entry: InstallEntry):
        yield

        
class PackageBase:
    def __init__(self, host:Host):
        pass

    def get_latest_version(self) -> str:
        '''
        返回该package最新可安装版本
        '''
        pass

    def get_installer(self) -> InstallerBase:
        '''
        返回InstallerBase的子类的一个实例，每次调用都应当构造一个新的实例
        '''
        pass 
