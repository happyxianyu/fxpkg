# -*- coding:utf-8 -*-
from dataclasses import dataclass
import dataclasses

from fxpkg.util import Path

from .constants import InstallState
import typing
from .types import VersionSetBase


_default_lst = lambda: dataclasses.field(default_factory=list)
_default_dict = lambda: dataclasses.field(default_factory=dict)

@dataclass
class InstallConfig:
    '''
    example:

    data_path = 'data/package/groupid/artifactid'
    download_path = 'cache/download/groupid/artifactid'
    build_path = 'cache/build/groupid/artifactid'
    '''
    libid: str = None
    version: typing.Union[str, VersionSetBase] = None
    compiler: str = None
    platform: str = None
    arch: str = None
    build_type: str = None
    other_key: dict = None

    install_path: Path = None  # 安装不可超出该目录
    # 以下为建议安装目录
    include_path: Path = None
    lib_path: Path = None
    bin_path: Path = None
    cmake_path: Path = None

    data_path: Path = None  # 该目录下的所有文件将持久保存
    # 以下为缓存目录
    download_path: Path = None
    build_path: Path = None
    tmp_path: Path = None

    toolset: set = _default_dict()
    # 环境变量
    env_vars: dict = _default_dict()

    other: dict = None  # 用于提供其他参数


class _InstallEntryBase:
    key_fields = ['libid', 'version', 'compiler', 'platform', 'arch', 'build_type', 'other_key']
    path_fields = ['install_path', 'include_path', 'lib_path', 'bin_path', 'cmake_path']
    val_fields = path_fields + ['lib_list', 'dll_list', 'dependent', 'dependency', 'install_state', 'other']


@dataclass
class InstallEntry(_InstallEntryBase):
    '''
    ''表示任意值
    None表示查询时任意值
    '''
    entry_id: int = None

    # key field
    libid: str = None
    version: str = None
    compiler: str = None
    platform: str = None
    arch: str = None
    build_type: str = None
    other_key: dict = None

    # value field
    install_path: Path = None  # 安装不可超出该目录
    # 以下为建议安装目录，可为空
    include_path: Path = None
    lib_path: Path = None
    bin_path: Path = None
    cmake_path: Path = None

    lib_list: list = None
    dll_list: list = None

    dependent: list = None
    dependency: list = None

    install_state: InstallState = None
    other: dict = None  # 用于保存其他信息



@dataclass
class LibUsingInfo:
    entries: dict = dataclasses.field(default_factory=dict)  # libids 到 entries的映射
    include_paths: list = _default_lst()
    lib_paths: list = _default_lst()
    bin_paths: list = _default_lst()
    cmake_paths: list = _default_lst()
    lib_list: list = _default_lst()
    dll_list: list = _default_lst()

    def append_entry(self, entry: InstallEntry, using_cmake = False):
        """
        若using_cmake，且cmake_path不为None，则会忽略其他路径
        """
        self.entries[entry.entry_id] = entry
        if entry.cmake_path is not None:
            self.cmake_paths.append(entry.cmake_path)
            if using_cmake:
                return

        if entry.include_path is not None:
            self.include_paths.append(entry.include_path)
        if entry.lib_path is not None:
            self.lib_paths.append(entry.lib_path)
        if entry.bin_path is not None:
            self.bin_paths.append(entry.bin_path)
        if entry.lib_list is not None:
            lib_list_set = set(self.lib_list)
            for lib in entry.lib_list:
                if lib not in lib_list_set:
                    self.lib_list.append(lib)
        if entry.dll_list is not None:
            dll_list_set = set(self.dll_list)
            for dll in entry.dll_list:
                if dll not in dll_list_set:
                    self.dll_list.append(dll)


del _default_lst

del dataclass
del Path
del InstallState
del VersionSetBase

del _InstallEntryBase
