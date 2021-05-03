# -*- coding:utf-8 -*-
import copy
import importlib
import dataclasses
import json
import logging
import typing
from collections import OrderedDict
import datetime
import random
import asyncio

import fxpkg.package

from .package import *
from fxpkg.db import *
from fxpkg.common.dataclass import *
from fxpkg.common import *
from fxpkg.util import *

from .util import parse_libid, get_sys_info

__all__ = [
    'LibManager',
    'ConfigManager',
    'PathManager',
    'InstallFailException',
    'PackageAlreadyExists',
]


class PackageAlreadyExists(Exception):
    pass


class InstallFailException(Exception):
    pass


def add_path_to_module(m, path):
    m.__path__.insert(0, str(path))


class PathManager:
    def __init__(self, root_path):
        root_path = Path(root_path)
        self.fxpkg_path = Path(__file__).prnt.prnt
        self.fxpkg_resource_path = self.fxpkg_path / 'resource'

        self.root_path = root_path

        self.pkg_install_path = root_path/'installed'
        self.pkg_download_path = root_path/'cache/download'

        self.paths = [
            self.pkg_install_path,

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
            self.pkg_download_path,
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

    def to_relative(self, path):
        path = Path(path)
        root_path = self.root_path
        if path.is_relative_to(root_path):
            return path.relative_to(root_path)
        else:
            return path

    def to_abs(self, path):
        path = Path(path)
        if path.is_absolute():
            return path
        root_path = self.root_path
        return root_path / path


    def get_pkg_path_info(self, info):
        libid = info.libid
        version = info.version
        groupid, artifactid = parse_libid(libid)
        lib_prefix = Path()/groupid/artifactid/version
        path_info=dict(
            install_path= self.pkg_install_path/lib_prefix,
            download_path = self.pkg_download_path/lib_prefix,
        )
        return path_info

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
            self.pathManager.fxpkg_resource_path.copy_to(self.pathManager.host_config_path)


class LibManager:
    def __init__(self, pathManager: 'PathManager', configManager: 'ConfigManager'):
        add_path_to_module(fxpkg.package, pathManager.package_path)
        self.pathManager = pathManager
        self.configManager = configManager
        self.repo = InstallInfoRepository(pathManager.installInfoDb_path)
        self._executors = {
            'initial': AsyncExecutor(workers_num=1),
            'download': AsyncExecutor(workers_num=3),
            'configure': AsyncExecutor(workers_num=1),
            'build': AsyncExecutor(workers_num=1),
            'install': AsyncExecutor(workers_num=1),
        }

    def get_package(self, libid) -> PackageBase:
        groupId, artifactId = parse_libid(libid)
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

    def _pre_proc_config(self, pkg:PackageBase, config:InstallConfig):
        assert config.libid is not None
        versions = pkg.get_versions()
        if config.version is None:
            for ver in versions:
                config.version = ver
        pathManager = self.pathManager
        config_d = DictObjectPorxy(config)
        config_d.update(pathManager.get_pkg_path_info(config))


    async def install_lib(self, config: InstallConfig):
        pkg = self.get_package(config.libid)
        self._pre_proc_config(pkg, config)
        installer = pkg.make_installer()
        entry = InstallEntry()

        prev_state = entry.install_state
        prev_stage = None
        installer.stage = 'initial'
        installer.config = config
        installer.entry = entry
        async for stage in installer.install(config, entry):
            logging.debug(stage)
            if False:
                entry = installer.entry
                if isinstance(stage, Exception):
                    pass
                    # TODO: 处理异常
                    entry.install_state = InstallState.FAIL_INSTALL
                    self.repo.update_entry_by_key_fields(entry)
                    return None

                installer.stage = stage
                state = entry.install_state
                if state != prev_state:
                    self.repo.update_entry_by_key_fields(entry)

                prev_stage = stage
                prev_state = state

        return entry

    async def request_lib(self, config: InstallConfig):
        """
        只识别key field和other，其他被忽略
        """
        pass

    async def request_libs(self, configs: typing.List[InstallConfig]):
        return [await self.request_lib(config) for config in configs]

    async def uninstall_lib(self, info: InstallEntry):
        """
        如果包裹提供了卸载方法，则使用pakcage的卸载方法
        否则，如果存在共享install_path，则会导致失败

        只识别 key field
        """
        pass

    async def submit_task(self, installer, task) -> asyncio.Future:
        executors = self._executors
        stage = installer.stage
        logging.debug(stage)
        future = await executors[stage].submit(task)
        return future

    def collect_using_info(self, entries: typing.List[InstallEntry], using_cmake=False) -> LibUsingInfo:
        """
        返回使用库所需的信息
        """
        repo = self.repo
        info = LibUsingInfo()
        visited_entryid = set()

        def collect(entry: InstallEntry):
            if entry.entry_id is None:
                entry = repo.get_by_key_fields(entry)
            if entry.entry_id in visited_entryid:
                return
            visited_entryid.add(entry.entry_id)
            if entry.libid in info.entries.keys():
                # TODO: version conflict
                return

            self.set_path_abs(entry)
            info.append_entry(entry, using_cmake=using_cmake)
            dependency = entry.dependency
            if dependency is not None:
                for entry_id in dependency:
                    dep_entry = repo.get_by_entry_id(entry_id)
                    collect(dep_entry)

        for entry in entries:
            collect(entry)
        return info

    def set_path_abs(self, entry: InstallEntry):
        entry_proxy = DictObjectPorxy(entry)
        for key in entry.path_fields:
            entry_proxy[key] = self.pathManager.to_abs(entry_proxy[path])
