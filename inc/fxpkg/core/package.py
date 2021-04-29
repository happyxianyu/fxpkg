# -*- coding:utf-8 -*-
from fxpkg.common.dataclass import InstallConfig
from .host import Host


class VersionSetBase:
    def __contains__(self, ver):
        return False

    def __iter__(self):
        '''
        返回可用版本，不一定要全面
        '''
        return iter()


class InstallerBase:
    async def download(self):
        r'''
        optional
        成功返回True，失败返回抛出异常
        如果因为配置失败，则更新config的ilegal fields
        如果实现，一次下载多个库可以同时编译和下载
        '''
        return True

    async def configure(self):
        pass

    async def build(self):
        '''
        optional
        成功返回True，失败返回抛出异常
        如果因为配置失败，则更新config的ilegal fields
        '''
    
    async def install(self):
        pass

    async def uninstall(self, libDesc):
        r'''
        成功返回True， 失败返回False
        '''
        return False

        
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
