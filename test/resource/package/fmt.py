import logging

from fxpkg import *

print = logging.debug

class Installer(InstallerBase):
    async def install(self, config: InstallConfig, entry: InstallEntry):
        yield 'download'
        git_url = 'https://github.com/fmtlib/fmt.git'
        print(config.download_path)
        print(git_url)
        future = await self.submit_task(git_clone_async(git_url,config.download_path))
        await future


class Package(PackageBase):
    def __init__(self, libManager: LibManager):
        super().__init__(libManager)
        logging.debug('load fmt')

    def get_versions(self):
        '''
        返回该package可安装版本
        '''
        return ['7.1.3']

    def make_installer(self) -> InstallerBase:
        return Installer(self.libManager)
