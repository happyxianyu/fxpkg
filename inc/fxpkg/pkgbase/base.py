import typing
from fxpkg import InstallConfig, InstallEntry, BuildContext

__all__ = ['PackageMgrBase', 'PackageMgr']

class PackageMgrBase:
    def set_config(self, config:'InstallConfig'):
        raise NotImplementedError

    async def request(self, config:'InstallConfig'=None) -> 'InstallEntry':
        raise NotImplementedError

    def get_dependency(self, config:'InstallConfig'=None):
        raise NotImplementedError





class PackageMgr(PackageMgrBase):
    def __init__(self, bctx: BuildContext, libid: str, git_url=None):
        if git_url is None:
            git_url = f'https://github.com/{libid}/{libid}.git'

        self.bctx = bctx
        self.libid = libid
        self.git_url = git_url

    def set_config(self, config: 'InstallConfig'):
        self.config = config
        build_type = config.build_type
        version = config.version

        self.repo_path = config.download_path
        self.build_path = config.build_path/version/build_type
        self.install_path = config.install_path/version/build_type
        self.log_path = config.log_path/version/build_type

        self.build_path.mkdir()
        self.install_path.mkdir()
        self.log_path.mkdir()


    def _set_config(self, config: 'InstallConfig'):
        if config is not None:
            self.set_config(config)

    async def request(self, config: InstallConfig = None):
            self._set_config(config)
            config = self.config
            libid = self.libid
            git_url = self.git_url
            build_type = config.build_type
            version = config.version
            repo_path = self.repo_path
            build_path = self.build_path
            install_path = self.install_path
            bctx = self.bctx
            run_light_proc = bctx.run_light_proc
            run_cmd_async = bctx.run_cmd_async
            run_heavy_proc = bctx.run_heavy_proc

            for p in (build_path, install_path):
                p.mkdir()

            # download
            await self.download()

            # configure
            await self.configure()

            # build
            await self.build()

            # install
            await self.install()
            return self.get_install_entry()

    def version_to_tag(self, version) -> str:
        return version
    
    async def configure():
        pass

    async def build():
        pass

    async def install():
        pass


    async def download(self, config: 'InstallConfig' = None):
        self._set_config(config)
        config = self.config
        libid = self.libid
        git_url = self.git_url
        version = config.version
        repo_path = self.repo_path

        bctx = self.bctx
        run_cmd_async = bctx.run_cmd_async
        run_download = bctx.run_download
        run_shellscript_async = bctx.run_shellscript_async
        run_light_download = bctx.run_light_download

        tag = self.version_to_tag(version)
        if not repo_path.exists():
            await run_download(run_cmd_async(f'git clone --depth=1 -b {tag} {git_url} {libid}', cwd=repo_path.prnt))
            assert repo_path.exists()
        else:   # fetch version and checkout
            await run_light_download(run_cmd_async(f'git fetch --depth=1 origin +refs/tags/{tag}:refs/tags/{tag}', cwd=repo_path))

    def get_install_entry(self, config:'InstallConfig' = None) -> 'InstallEntry':
        self._set_config(config)
        config = self.config
        install_path = self.install_path
        install_entry = InstallEntry()
        install_entry.install_path = install_path
        install_entry.include_path = install_path/'include'
        install_entry.lib_path = install_path/'lib'
        install_entry.cmake_path = install_path/'lib/cmake'
        return install_entry

