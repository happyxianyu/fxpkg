# -*- coding:utf-8 -*-
from dataclasses import dataclass
from fxpkg.util import Path

@dataclass
class LibDesc:
    '''lib描述信息，用于区分库'''
    name:str = None
    version:str = None
    platform:str = None
    arch:str = None
    build_type:str = None


@dataclass
class LibUsingInfos:
    include_paths:list = None
    lib_paths:list = None
    bin_paths:list = None
    lib_names:list = None
    cmake_paths:list = None


@dataclass
class InstallConfig:
    name:str = None
    version:str = None
    platform:str = None
    arch:str = None
    build_type:str = None

    install_path:Path = None #安装不可超出该目录
    #以下为建议安装目录
    include_path:Path = None
    lib_path:Path = None
    bin_path:Path = None
    cmake_path:Path = None
    
    data_path:Path = None   #该目录下的所有文件将持久保存
    #以下为缓存目录
    download_path:Path = None
    build_path:Path = None
    tmp_path:Path = None
    log_path:Path = None

    other:dict = None #other为package自定义需要的信息

    
@dataclass
class InstallEntry:
    id:int = None
    name:str = None
    version:str = None
    platform:str = None
    arch:str = None
    build_type:str = None

    include_path:Path = None 
    lib_path:Path = None
    bin_path:Path = None
    cmake_path:Path = None

    dependent:list = None #其中元素为被依赖库的id
    dependency:list = None #其中元素为依赖库的id
    other:object = None    #other为package自定义存储的其他信息

@dataclass
class InstallEntryInfo:
    id:int = None
    include_paths:Path = None
    lib_path:Path = None
    bin_path:Path = None
    cmake_path:Path = None

    dependent:list = None  #其中元素为依赖库的id
    other:object = None    #other为package自定义存储的其他信息