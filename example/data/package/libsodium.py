from cbutil import Path
from fxpkg import *
from fxpkg.pkgbase import *
from fxpkg.helpler import *





libid = 'libsodium'
git_url = 'https://github.com/jedisct1/libsodium.git'


class LibsodiumMgr(GitPkgMgr):
    def __init__(self, bctx: BuildContext):
        super().__init__(bctx, libid, git_url)
    
    async def install(self):
        pass

    

    async def build(self):
        log_path = self.log_path
        config = self.config
        repo_path = self.repo_path
        bctx = self.bctx
        run_heavy_proc = bctx.run_heavy_proc
        run_shellscript_async = bctx.run_shellscript_async
        msvc_info_proxy = MSVCInfoProxy(config.toolset.choose_msvc())
        # use buildall.bat and buildbase.bat to build
        build_tool_path = repo_path/r'builds\msvc\build'
        # get the command line we want
        buildall_bat=build_tool_path/'buildall.bat'
        async with AIOFile(buildall_bat, 'r') as f:
            content = await f.read()
        ver_num = msvc_info_proxy.install_version.split('.')[0]
        cmd = None
        for cmd in content.splitlines():
            if cmd[-2:].strip() == ver_num:
                break
        else:
            assert False
        bat_script = f'''
CD {build_tool_path.quote}
SET my_environment={msvc_info_proxy.vcvarsall.quote}
{cmd}
'''
        await run_heavy_proc(run_shellscript_async(bat_script, cwd=build_tool_path))
        
        # move logs
        for f in build_tool_path.file_son_iter:
            f:Path
            if f.ext == 'log':
                f.move_to(log_path)


    async def configure(self):
        await super().configure()
        repo_path = self.repo_path

        # use buildall.bat and buildbase.bat to build
        build_tool_path = repo_path/r'builds\msvc\build'
        # replace !environment! to !my_environment! in buildbase.bat
        async with AIOFile(build_tool_path/'buildbase.bat', 'r+') as f:
            content = await f.read()
            if '!my_environment!' not in content:
                content = content.replace('!environment!', '!my_environment!')
                content = content.replace('%environment%', '!my_environment!')
                await f.write(content)


        
def get_package_mgr(bctx:BuildContext):
    return LibsodiumMgr(bctx)


