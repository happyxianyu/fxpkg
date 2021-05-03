import copy
import dataclasses

from fxpkg.common import InstallConfig


__all__ = ['LibManagerOutHandler',
           'DefaultLibManagerOutHandler']

class LibManagerOutHandler:
    """
    libManager的输出接口
    """
    def __init__(self, **kwargs):
        pass

    def install_begin(self, id_:int , config: InstallConfig, **kwargs):
        """
        开始安装
        初始时state == 'initial'
        """
        pass

    def update_install_state(self, id_: int, state: str, info=None, **kwargs):
        """
        一定会在install_begin后调用
        每个config一定对应一个install
        install_begin传入id(config)，为了减少拷贝开销
        state == 'done' 时表示完成, 此时info为InstallEntry
        state == 'fail' 时表示失败，此时info为Exception
        """
        pass

    def update_progress(self, id_: int, size=None, total=None, info=None, tag=None, **kwargs):
        """
        一定会在install_begin后调用
        更新进度
        size表示已完成大小
        total表示总大小
        """
        pass

    async def fix(self, id_, error: Exception, **kwargs):
        """
        安装失败时调用，等待用户修复
        成功返回更新后端config
        失败返回None
        """
        return None


class DefaultLibManagerOutHandler(LibManagerOutHandler):
    def __init__(self):
        self.trace_infos = {}

    def install_begin(self, id_: int, config: InstallConfig, **kwargs):
        @dataclasses.dataclass
        class ConfigEx(InstallConfig):
            state: str = 'initial'

        config = ConfigEx(**dataclasses.asdict(config))
        self.trace_infos[id_] = config
        print(f'Begin Install: {config.libid}, {dataclasses.asdict(config)}')

    def update_install_state(self, id_: int, state: str, info=None, **kwargs):
        config = self.trace_infos[id_]
        config.state = state
        if state == 'fail':
            print(f'Fail to install: {config.libid}, Error: {info}')
        else:
            print(f'install state updating: {config.libid}, {config.state}')

    def update_progress(self, id_: int, size=None, total=None, info=None, tag=None, **kwargs):
        config = self.trace_infos[id_]
        print(f'update progress: {config.libid}, {size}, {total}, {info}, {tag}')

    async def fix(self, id_, error: Exception, **kwargs):
        """
        安装失败时调用，等待用户修复
        成功返回更新后端config
        失败返回None
        """
        config = self.trace_infos[id_]
        print(f'fix: {config.libid}')
        return None
