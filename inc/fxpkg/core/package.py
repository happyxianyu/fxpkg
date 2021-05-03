# -*- coding:utf-8 -*-
import asyncio

from fxpkg.common.dataclass import InstallConfig
from fxpkg.common.types import VersionSetBase
from fxpkg.common import *

class InstallerBase:
    def __init__(self, libManager : 'LibManager'):
        self.libManager = libManager
        self.stage: str = 'initial'
        self.config: InstallConfig = None
        self.entry: InstallEntry = None
        self.reserved = None

    async def install(self, config: InstallConfig, entry: InstallEntry):
        yield

    def submit_task(self, task) -> asyncio.Future:
        return self.libManager.submit_task(task, self.stage)

    def show_progress(self, size=None, total=None, info=None, tag=None):
        pass

        
class PackageBase:
    def __init__(self, libManager : 'LibManager'):
        self.libManager = libManager

    def get_versions(self) -> VersionSetBase:
        '''
        返回该package安装版本
        '''
        pass

    def make_installer(self) -> InstallerBase:
        '''
        创建InstallerBase的子类的一个实例
        '''
        pass

