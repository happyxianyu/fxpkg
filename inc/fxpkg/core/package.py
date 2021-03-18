# -*- coding:utf-8 -*-
from .dataclass import InstallConfig
from .manager import LibManager

class PackageBase:
    def __init__(self, libManager:LibManager):
        pass

    def get_latest_version(self):
        '''
        返回该package最新可安装版本
        '''
        pass

    def get_config(self):
        '''
        返回ConfigurerBase的子类的一个实例，每次调用都应当构造一个新的实例
        '''
        pass

    def get_installer(self):
        '''
        返回InstallerBase的子类的一个实例，每次调用都应当构造一个新的实例
        '''
        pass 

class VersionSetBase:
    def __contains__(self, ver):
        return False

    def __iter__(self):
        '''
        返回可用版本，不一定要全面
        '''
        return iter()

class ConfigurerBase:
    def set_configInfo(self, configInfo:InstallConfig):
        self.configInfo = configInfo

    def get_dependency(self):
        '''
        返回构建依赖表, 由list存储，其中每个元素为(name, version_range)，要求依赖顺序正确，左边依赖右边
        '''
        pass

    def get_conflicts(self):
        '''
        返回冲突的库
        '''
        return True

    def fix_and_complete(self, option = None):
        '''
        optional
        将无效信息修正，并自动补全必需信息
        该方法会在dependency安装完成后调用
        '''
        pass

    def get_alternate_dependency_by_libDesc(self, libDesc):
        '''
        optional
        返回一个libDesc的替换的迭代器
        用于安装某一版本失败时的补救措施
        '''
        return iter()

    def is_legal(self):
        return False

    def get_ilegal_fields(self):
        '''
        optional
        返回非法域
        '''

    def get_options_by_field(self, field):
        '''
        optional
        返回对应field的选项
        '''
        pass



class InstallerBase:
    def set_configurer(self, configurer:ConfigurerBase):
        self.configurer = configurer
        self.has_download_flag = (InstallerBase.download == self.download)

    async def install(self):
        r'''
        成功返回list[InstallEntryInfo]，忽略id和dependent属性，
        dependency记录使用依赖id，如果找不到对应的dependency可以不记录

        失败抛出异常
        如果因为配置失败，则更新config的ilegal fields
        '''
        pass

    async def install_alone(self):
        r'''
        给予独立文件夹安装
        '''
        return False

    async def uninstall(self, libDesc):
        r'''
        成功返回True， 失败返回False
        '''
        return False

    async def build(self):
        '''
        optional
        成功返回True，失败返回抛出异常
        如果因为配置失败，则更新config的ilegal fields
        '''

    async def download(self):
        r'''
        optional
        成功返回True，失败返回抛出异常
        如果因为配置失败，则更新config的ilegal fields
        如果实现，一次下载多个库可以同时编译和下载
        '''
        return True


        