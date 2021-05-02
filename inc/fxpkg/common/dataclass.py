# -*- coding:utf-8 -*-
from dataclasses import dataclass

from fxpkg.util import Path

from .constants import InstallState
import typing
from .types import VersionSetBase



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

    other: dict = None  # 用于提供其他参数


@dataclass
class InstallEntry:
    '''
    用''表示空
    None表示任意
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
    # 以下为建议安装目录
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
class LibUsingInfos:
    include_paths: list = None
    lib_paths: list = None
    bin_paths: list = None
    lib_names: list = None
    cmake_paths: list = None


del dataclass
del Path
del InstallState
del VersionSetBase
