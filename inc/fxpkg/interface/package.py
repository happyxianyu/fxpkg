# -*- coding:utf-8 -*-
import asyncio
import typing

from fxpkg.common import *


class InstallerBase:
    def __init__(self, libManager: 'LibManager'):
        self.libManager = libManager
        self.stage: str = 'initial'
        self.config: InstallConfig = None
        self.entry: InstallEntry = None
        self.dependency = {}  # libid, installerBase

    async def install(self, config: InstallConfig, entry: InstallEntry):
        yield

    def get_dependency(self):
        """
        保证config已经设置
        {
        libid : VersionSet
        }
        """
        return {}

    async def acquire(self, libid: str):
        pass

    def submit_task(self, task) -> asyncio.Future:
        return self.libManager.submit_task(task, self.stage)

    def show_progress(self, size=None, total=None, info=None, tag=None):
        pass


class PackageBase:
    def __init__(self, libManager: 'LibManager'):
        self.libManager = libManager

    def get_versions(self) -> typing.List[str]:
        """
        返回该package安装版本
        """
        pass

    def get_dependency(self) -> typing.List[str]:
        """
        返回所有版本依赖libid的并集 [libid, ...]
        """
        return []

    def make_installer(self, version=None) -> InstallerBase:
        '''
        创建InstallerBase的子类的一个实例
        '''
        pass

