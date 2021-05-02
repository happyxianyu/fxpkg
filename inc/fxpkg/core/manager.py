# -*- coding:utf-8 -*-
import copy
import importlib
import dataclasses
import json
from collections import OrderedDict
import datetime
import random
import asyncio
from fxpkg.util import *

import fxpkg.package
from fxpkg.db import *
from fxpkg.common.dataclass import *
from .util import parse_libid, get_sys_info


class PackageAlreadyExists(Exception):
    pass


class InstallFailException(Exception):
    pass


def add_path_to_module(m, path):
    m.__path__.insert(0, str(path))


class PathManager:
    def __init__(self, root_path):
        root_path = Path(root_path)
        self.root_path = root_path
        self.paths = [
            root_path / 'installed',

            root_path / 'data',
            root_path / 'data/host',
            root_path / 'data/package',

            root_path / 'package',
            root_path / 'package/main',

            root_path / 'config',

            root_path / 'log',
            root_path / 'log/package',
            root_path / 'log/host',

            root_path / 'cache',
            root_path / 'cache/tmp',
            root_path / 'cache/tmp/messey',
            root_path / 'cache/tmp/host',
            root_path / 'cache/tmp/package',
            root_path / 'cache/download',
            root_path / 'cache/build'
        ]
        self.paths = [Path(p) for p in self.paths]
        self.package_path = root_path / 'package'
        self.installInfoDb_path = root_path / 'data/host/installInfo.db'
        self.tmp_messey_path = root_path / 'cache/tmp/messey'
        self._init()

    def _init(self):
        '''创建本体目录'''
        for p in self.paths:
            p.mkdir()
        self.init_pkgs()

    def init_pkgs(self):
        pkg_path = self.package_path
        for p in pkg_path.dir_son_iter:
            if '__init__.py' not in (p1.name for p1 in p.file_son_iter):
                (p / '__init__.py').touch()

    def reinit(self):
        '''删除并重新创建本体目录'''
        self.root_path.remove_sons()
        self.init_pkgs()

    def get_install_path(self, groupId='main', artifactId='__default', version=None):
        root_path = self.root_path
        if version != None:
            return root_path / 'installed' / groupId / artifactId / version
        else:
            return root_path / 'installed' / groupId / artifactId

    def create_tmpfile(self):
        prnt = self.tmp_messey_path()
        while True:
            rand_val = random.randint(0, 1 << 64)
            name = str(datetime.datetime.now()) + ' ' + hex(rand_val)
            p = prnt / name
            if not p.exists():
                break
        p.touch()
        return p

    @property
    def host_config_path(self):
        return self.root_path / 'host-config.json'


class ConfigManager:
    def __init__(self, pathManager: PathManager):
        self.pathManager = pathManager
        self.host_config = self.load_host_config()

    def load_host_config(self):
        self.create_host_config()
        with self.pathManager.host_config_path.open('r') as fr:
            config = json.load(fr)
        return config

    def create_host_config(self):
        if not self.pathManager.host_config_path.exists():
            (Path(__file__).prnt.prnt / 'resource/host-config.json').copy_to(self.pathManager.host_config_path)


class LibManager:
    def __init__(self, pathManager: 'PathManager', configManager: 'ConfigManager'):
        add_path_to_module(fxpkg.package, pathManager.package_path)
        self.pathManager = pathManager
        self.configManager = configManager
        self.repo = InstallInfoRepository(pathManager.installInfoDb_path)

    def get_package(self, artifactId, groupId='main'):
        m = importlib.import_module(f'fxpkg.package.{groupId}.{artifactId}')
        return m.Package(self)

    def add_package(self, src, groupId='main', overwrite=True):
        """
        将package拷贝到对应目录
        若overwrite为False，当目标存在时，会raise PackageAlreadyExists
        """
        src = Path(src)
        dst = self.pathManager.package_path / groupId
        if not overwrite:
            (dst / src.name).exists()
            raise PackageAlreadyExists()
        if not dst.exists():
            dst.mkdir()
            (dst / '__init__.py').touch()
        src.copy_to(dst, is_prefix=True)

    async def request_lib(self, config: InstallConfig):
        """
        只识别key field和other，其他被忽略
        """
        pass

    async def uninstall_lib(self, info: InstallEntry):
        """
        如果包裹提供了卸载方法，则使用pakcage的卸载方法
        否则，如果存在共享install_path，则会导致失败

        只识别 key field
        """
        pass

    def submit_task(self, coro):
        pass
