# -*- coding:utf-8 -*-
import base64
import copy
import importlib
import dataclasses
import io
import json
import logging
import typing
import datetime
import random
import os
import time
import platform
import asyncio
import subprocess
from collections import ChainMap
from functools import cached_property

import dotenv
import aiofile
import more_itertools

import fxpkg.package
from fxpkg.db import *
from fxpkg.common.dataclass import *
from fxpkg.common import *
from fxpkg.util import *

from .package import *
from .output import *

from .util import parse_libid, get_sys_info

__all__ = [
    'LibManager',
    'ConfigManager',
    'PathManager',
    'NotSupportError',
    'InstallFailException',
    'PackageAlreadyExists',
]

_time_start = time.time_ns()

class NotSupportError(Exception):
    pass

class PackageAlreadyExists(Exception):
    pass


class InstallFailException(Exception):
    pass


class LocalException(Exception):
    """
    内部使用
    """
    pass



def add_path_to_module(m, path):
    m.__path__.insert(0, str(path))


class PathManager:
    def __init__(self, root_path):
        root_path = Path(root_path)
        self.fxpkg_path = Path(__file__).prnt.prnt
        self.fxpkg_resource_path = self.fxpkg_path / 'resource'

        self.root_path = root_path
        self.host_data_path = root_path / 'data/host/'

        self.tmp_path = root_path / 'cache/tmp'
        self.tmp_messy_path = root_path / 'cache/tmp/messy'

        self.pkg_install_path = root_path / 'installed'
        self.pkg_download_path = root_path / 'cache/download'
        self.pkg_build_path = root_path / 'cache/build'

        self.paths = [
            self.pkg_install_path,

            root_path / 'data',
            self.host_data_path,
            root_path / 'data/package',

            root_path / 'package',
            root_path / 'package/main',

            root_path / 'config',

            root_path / 'log',
            root_path / 'log/package',
            root_path / 'log/host',

            root_path / 'cache',
            root_path / 'cache/tmp',
            self.tmp_messy_path,
            root_path / 'cache/tmp/host',
            root_path / 'cache/tmp/package',
            self.pkg_download_path,
            self.pkg_build_path
        ]

        self.paths = [Path(p) for p in self.paths]
        self.package_path = root_path / 'package'
        self.install_info_repo_path = self.host_data_path / 'install_info'
        self.tmp_messey_path = root_path / 'cache/tmp/messey'

        self.global_config_path = self.root_path / 'config.json'
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


    @staticmethod
    def make_tmp_name():
        count = _time_start + time.perf_counter_ns()
        bs = count.to_bytes(count.bit_length()//8+1, 'big')
        name = base64.b64encode(bs).decode('ascii')
        return name

    def make_tmp_path(self, suffix='', prefix=''):
        messy_path = self.tmp_messy_path
        return messy_path / (prefix + self.make_tmp_name() + suffix)

    def to_relative(self, path):
        """
        将路径转换为相对于root_path的相对路径
        """
        path = Path(path)
        root_path = self.root_path
        if path.is_relative_to(root_path):
            return path.relative_to(root_path)
        else:
            return path

    def to_abs(self, path):
        """
        将路径转换为相对于root_path的绝对路径
        """
        path = Path(path)
        if path.is_absolute():
            return path
        root_path = self.root_path
        return root_path / path

    def get_pkg_path_info(self, info, prefix=None):
        """
        install_path: installed/ groupid / artifactid / version
        """
        libid = info.libid
        version = info.version
        groupid, artifactid = parse_libid(libid)
        if prefix is None:
            lib_prefix_path = Path() / groupid / artifactid / version
        else:
            lib_prefix_path = Path() / groupid / artifactid / prefix
        lib_install_prefix = self.pkg_install_path / lib_prefix_path
        path_info = dict(
            install_path=lib_install_prefix,
            include_path=lib_install_prefix / 'include',
            bin_path=lib_install_prefix / 'bin',
            lib_path=lib_install_prefix / 'lib',
            cmake_path=lib_install_prefix / 'lib/cmake',
            download_path=self.pkg_download_path / lib_prefix_path,
            build_path=self.pkg_build_path / lib_prefix_path,
        )
        return path_info

    def close(self):
        # clear tmp
        try:
            self.tmp_path.remove_sons()
            logging.warning('Fail to delete tmp')
        except IOError:
            pass



class ConfigManager:
    def __init__(self, pathManager: PathManager):
        self.pathManager = pathManager
        self.global_config = self.load_global_config()

    def find_tools(self, name, version=None):
        results = []
        tools = self.global_config['tools']
        for tool in tools:
            if name != tool['name']:
                continue
            if version is not None:
                tool_version: str = tool.get('version')
                if tool_version is None \
                        or tool_version.startswith(version):
                    results.append(tool)
        return results

    def load_global_config(self, str2path=True):
        """
        若str2path为True，则会将符合条件的值转为Path
        """
        self.create_global_config()
        with self.pathManager.global_config_path.open('r') as fr:
            global_config = json.load(fr)

        # proc path
        if str2path:
            def _str2path(item):
                if isinstance(item, dict):
                    d: dict = item
                    for k, v in d.items():
                        k: str
                        if k.endswith('_path'):
                            if isinstance(v, list):
                                d[k] = list(map(Path, v))
                            elif isinstance(v, str):
                                d[k] = Path(v)
                    _str2path(v)
                elif isinstance(item, list):
                    lst: list = item
                    for x in lst:
                        _str2path(x)

            _str2path(global_config)

        # proc tools
        tools = global_config['tools']
        tools_map = {}  # id: tool
        global_config['tools_map'] = tools_map
        for tool in tools:
            tool: dict
            if tool.get('name') == 'msvc':
                aux_build_path = tool['install_path'] / 'VC/Auxiliary/Build'
                tool.setdefault('aux_build_path', aux_build_path)

            tool_id = tool.get('id')
            if tool_id is not None:
                tools_map[tool_id] = tool

        # proc toolsets
        toolsets: dict = global_config['toolsets']
        for toolset_id, toolset in toolsets.items():
            # 处理引用
            refs = []
            for tool_id in toolset:
                assert isinstance(tool_id, str)
                refs.append(tools_map[tool_id])
            toolsets[toolset_id] = refs

        # proc install_configs
        install_configs = global_config['install_configs']
        self._proc_inherits(install_configs)
        for install_config in install_configs.values():
            install_config: dict

            # toolset默认值
            install_config.setdefault('toolset', toolsets.get('default'))
            toolset: str = install_config['toolset']
            # 处理引用
            if isinstance(toolset, str):
                toolset_id = toolset
                install_config['toolset'] = toolsets[toolset_id]
            # 设置附加信息
            toolset: set = install_config['toolset']
            for tool in toolset:
                if tool['name'] == 'msvc':
                    install_config.setdefault('compiler', 'cl')
                    # install_config.setdefault('generator', 'msvc')
        logging.debug(f'loading global config: {global_config}')
        return global_config

    def create_global_config(self, overwrite=False):
        if not self.pathManager.global_config_path.exists():
            src_global_config_path = self.pathManager.fxpkg_resource_path / 'config.json'
            print(src_global_config_path)
            if not src_global_config_path.exists() or overwrite:
                global_config = self.make_global_config()
                with src_global_config_path.open('w') as fw:
                    json.dump(global_config, fw, indent=4)
            src_global_config_path.copy_to(self.pathManager.global_config_path)

    def make_global_config(self):
        default_config = {
            # 'inherits' : 'config_x',
            "build_type": "release",
            'platform': self.host_platform,
            'arch': self.host_arch,
            # 'toolset' : 'msvc_1'  #若未指定，则为default
        }

        global_config = {
            'install_configs': {
                'default': default_config
            },
            'toolsets': {
                'default': {}
                # toolset是一个包含多个tool的集合
                # 如果在windows平台上，default必须包含msvc，因为需要依赖msvc运行时
                # 例:
                # 'default' : {'msvc_1'}
            },

            "tools": [
                # 填入构建工具信息
                # 例:
                # {
                #     "id" : "msvc_1"
                #     "name" : "msvc",
                #     "version" : "1.7",
                #     "install_path" : "path"
                # }
            ]
        }

        tools = global_config['tools']
        id_suffix = 1

        if default_config['platform'] == 'windows':
            msvc_tool_infos = self._get_msvc_tool_infos()
            if len(msvc_tool_infos) != 0:
                # set id
                for info in msvc_tool_infos:
                    info['id'] = f'msvc_{id_suffix}'
                    id_suffix += 1
                global_config['toolsets']['default'] = ['msvc_1']
                tools += msvc_tool_infos

        return global_config

    def _get_msvc_tool_infos(self, id_suffix=1):
        msvc_installer_path = Path() / os.environ['ProgramFiles(x86)'] / 'Microsoft Visual Studio/Installer'
        if not msvc_installer_path.exists():
            return []

        print(msvc_installer_path)

        with subprocess.Popen([msvc_installer_path / 'vswhere.exe', '-format', 'json', '-utf8'],
                              cwd=msvc_installer_path,
                              stdout=subprocess.PIPE) as proc:
            stdout, stderr = proc.communicate()

        try:
            msvc_infos: list = json.loads(stdout)
        except json.JSONDecodeError:
            return []

        msvc_tool_infos = []
        for msvc_info in msvc_infos:
            msvc_install_path = Path(msvc_info['installationPath'])
            msvc_aux_build_path = msvc_install_path / 'VC/Auxiliary/Build'

            msvc_tool_info = {
                'id': None,
                "name": "msvc",
                "version": msvc_info['installationVersion'],
                'line_version': msvc_info['catalog']['productLineVersion'],
                "instance_id": msvc_info['instanceId'],
                "display_name": msvc_info['displayName'],
                'install_path': str(msvc_install_path),
            }
            msvc_tool_infos.append(msvc_tool_info)
        return msvc_tool_infos

    @staticmethod
    def _proc_inherits(d: dict):
        """
        将存在继承的值转换为ChainMap
        """
        keys = d.keys()
        for k, v in d.items():
            v: dict
            base_ids = v.get('inherits', [])
            for base_id in base_ids:
                base = d[base_id]
                if isinstance(base, ChainMap):
                    d[k] = ChainMap(v, *base.maps)
                else:
                    d[k] = ChainMap(v, base)

    @cached_property
    def host_arch(self):
        _arch_map = {
            'amd64': 'x86_64',
            'x64': 'x86_64'
        }

        arch = platform.machine().lower()
        arch = _arch_map.get(arch, arch)
        return arch

    @cached_property
    def host_platform(self):
        platform_ = platform.system().lower()
        return platform_

    async def fill_install_config_and_entry(self, config: InstallConfig, entry: InstallEntry = None):
        assert config.libid is not None
        assert config.version is not None
        pathManager = self.pathManager
        config_d = DictObjectPorxy(config)
        default_install_config = self.global_config['install_configs']['default']

        keys = dataclasses.fields(config)

        def update_cond(k, v):
            return config_d.get(k) is None and k in keys

        config_d.update(default_install_config, cond=update_cond)
        config_d.update(pathManager.get_pkg_path_info(config), cond=update_cond)
        arch = config.arch

        toolset = config_d['toolset']

        for tool in toolset:
            if tool['name'] == 'msvc':
                try:  # get env vals
                    envfile = pathManager.make_tmp_path()
                    aux_build_path: Path = tool['aux_build_path']
                    vcvarsall = aux_build_path / 'vcvarsall.bat'
                    script = f'''
cd {aux_build_path.quote()}
call {vcvarsall.quote()} {arch}
set > {envfile.quote()}
'''
                    await run_shellscript_async(script, pathManager.make_tmp_path(suffix='.bat'))
                    async with aiofile.AIOFile(envfile, 'r') as fr:
                        content = await fr.read()
                    stream = io.StringIO(content)
                    env_vals = dotenv.dotenv_values(stream)
                    if isinstance(env_vals, dict):
                        config.env_vars = env_vals
                    break
                except IOError as e:
                    logging.warning(e)
        if entry is not None:
            keys = dataclasses.fields(entry)
            entry_d = DictObjectPorxy(entry)

            def update_cond(k, v):
                return entry_d.get(k) is None and k in keys

            entry_d.update(dataclasses.asdict(config), cond=update_cond)


class LibManager:
    def __init__(self,
                 pathManager: 'PathManager',
                 configManager: 'ConfigManager',
                 outHandler: LibManagerOutHandler = None):
        if outHandler is None:
            self._outHandler = DefaultLibManagerOutHandler()

        add_path_to_module(fxpkg.package, pathManager.package_path)
        self.pathManager = pathManager
        self.configManager = configManager
        self.repo = InstallInfoRepository(pathManager.install_info_repo_path)
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

    async def _proc_config_and_entry(self, pkg: PackageBase, config: InstallConfig, entry: InstallEntry = None):
        assert config.libid is not None
        if config.version is None:
            config.version = more_itertools.first(pkg.get_versions(), None)
        pathManager = self.pathManager
        configManager = self.configManager
        await configManager.fill_install_config_and_entry(config, entry)

    async def install_lib(self, config: InstallConfig):
        """
        通常不应当直接调用此方法，而是应当调用require_lib
        config只需要提供libid即可，其他都是可选的
        """
        pkg = self.get_package(config.libid)
        installer = pkg.make_installer()
        entry = InstallEntry()
        await self._proc_config_and_entry(pkg, config, entry)

        prev_state = entry.install_state
        prev_stage = None
        installer.stage = 'initial'
        installer.config = config
        installer.entry = entry
        self._outHandler.install_begin(id(installer), config)
        async for stage in installer.install(config, entry):
            if False:
                entry = installer.entry
                if isinstance(stage, Exception):
                    pass
                    # TODO: 处理异常

                installer.stage = stage
                state = entry.install_state
                if state != prev_state:
                    self.repo.update_entry_by_key_fields(entry)

                prev_stage = stage
                prev_state = state
        self._outHandler.update_install_state(id(installer), 'done', installer.entry)

        return entry

    async def request_lib(self, config: InstallConfig, installer: InstallerBase = None):
        """
        只识别key field和other，其他被忽略
        installer用于探测依赖，对于package，应当把自身传入
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

    def submit_task(self, task, stage: str) -> asyncio.Future:
        executors = self._executors
        future = executors[stage].submit_nw(task)
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

    def show_progress(self, installer, size=None, total=None, info=None, tag=None):
        self._outHandler.update_progress(id(installer), size, total, info, tag)
