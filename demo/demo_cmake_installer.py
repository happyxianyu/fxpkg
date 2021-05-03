from fxpkg.core import LibManager
from fxpkg.core.package import *
from fxpkg.common.dataclass import *
from fxpkg.util import *

class CMakeInstaller(InstallerBase):
    def __init__(self, libManager : LibManager):
        super().__init__(libManager)

    async def install(self, config: InstallConfig, entry: InstallEntry):
        '''
        通过entry传递安装信息
        '''
        libManager = self.libManager

        yield 'download'
        url = ''
        config.build_path.mkdir()
        cwd = config.build_path
        download_future = self.submit_task(git_clone_async(url, cwd))

        yield 'dependency'
        dependency = []
        futures = [await self.submit_task(libManager.request_lib(dep)) for dep in dependency]

        dep_entries = [await future for future in futures]
        await download_future
        yield 'configure'
        using_info: LibUsingInfo = libManager.collect_using_info(dep_entries, using_cmake=True)
        config = self.config
        private_path = config.build_path/Path('_fxpkg_private')
        shell_script = 'cmake -DCMAKE_PREFIX_PATH={} -DCMAKE_INSTALL_PREFIX={} -B {private_path.excape_str}'

        yield 'build'

        yield 'install'

        #TODO


