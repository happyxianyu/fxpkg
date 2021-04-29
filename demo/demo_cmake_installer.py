from fxpkg.core.host import Host
from fxpkg.core.package import *
from fxpkg.common.dataclass import InstallConfig
from fxpkg.util import *

class CMakeInstaller(InstallerBase):
    def __init__(self, host:Host, config:InstallConfig):
        self.host = host
        self.config = config

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
        config = self.config
        private_path = config.build_path/Path('_fxpkg_private')
        shell_script = 'cmake -DCMAKE_PREFIX_PATH={} -DCMAKE_INSTALL_PREFIX={} -B {private_path.excape_str}'
        #TODO
    
    async def install(self):
        pass

    async def uninstall(self, libDesc):
        r'''
        成功返回True， 失败返回False
        '''
        return False

        
