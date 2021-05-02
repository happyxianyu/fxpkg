from fxpkg.core import LibManager
from fxpkg.core.package import *
from fxpkg.common.dataclass import *
from fxpkg.util import *

class CMakeInstaller(InstallerBase):
    def __init__(self, libManager : LibManager):
        self.libManager = libManager

    async def install(self, config: InstallConfig, entry: InstallEntry):
        '''
        通过entry传递安装信息
        '''
        libManager = self.libManager

        yield 'download'

        yield 'dependency'


        yield 'configure'

        yield 'build'

        yield 'install'

        config = self.config
        private_path = config.build_path/Path('_fxpkg_private')
        shell_script = 'cmake -DCMAKE_PREFIX_PATH={} -DCMAKE_INSTALL_PREFIX={} -B {private_path.excape_str}'
        #TODO

