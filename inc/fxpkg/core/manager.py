# -*- coding:utf-8 -*-
import importlib
import dataclasses
import json
from collections import OrderedDict
import datetime
import random

from fxpkg.util import Path
import fxpkg.package
from fxpkg.db import *
from .dataclass import *
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
            root_path/'installed',
            root_path/'data',
            root_path/'data/host',
            root_path/'package',
            root_path/'package/main',
            root_path/'config',
            root_path/'log',
            root_path/'cache',
            root_path/'cache/tmp',
            root_path/'cache/tmp/messey',
            root_path/'cache/tmp/host',
            root_path/'cache/tmp/package',
            root_path/'cache/download',
            root_path/'cache/build'
        ]
        self.paths = [Path(p) for p in self.paths]
        self.package_path = root_path/'package'
        self.installInfoDb_path = root_path/'data/host/installInfo.db'
        self.tmp_messey_path = root_path/'cache/tmp/messey'
        self.initialize()


    def initialize(self):
        '''创建本体目录'''
        for p in self.paths:
            p.mkdir()
        self.initialize_packages()

    def initialize_packages(self):
        pkg_path = self.package_path
        for p in pkg_path.dir_son_iter:
            if '__init__.py' not in (p1.name for p1 in p.file_son_iter):
                (p/'__init__.py').touch()
        

    def re_initialize(self):
        '''删除并重新创建本体目录'''
        self.root_path.remove_sons()
        self.initialize_packages()

    def get_install_path(self, groupId = 'main', artifactId = '__default', version = None):
        root_path = self.root_path
        if version != None:
            return root_path/'installed'/groupId/artifactId/version
        else:
            return root_path/'installed'/groupId/artifactId
            

    def fill_installConfig(self, config):
        '''
        根据configInfo.name填充值路径信息
        '''
        pass

    def create_tmpfile(self):
        prnt = self.tmp_messey_path()
        while True:
            rand_val = random.randint(0, 1<<64)
            name = str(datetime.datetime.now()) + ' ' + hex(rand_val)
            p = prnt/name
            if not p.exists():
                break
        p.touch()
        return p


class LibManager:
    def __init__(self, host):
        pathManager = host.pathManager
        add_path_to_module(fxpkg.package, pathManager.package_path)
        self.pathManager = pathManager
        self.configManager = host.configManager
        self.repo = InstallInfoRespository(pathManager.installInfoDb_path)

    def get_using_infos(self, libDescs):
        '''
        返回LibUsingInfos
        lib_names要求顺序正确，左边的依赖右边的
        '''
        pass

    def get_using_infos_by_names(self, names, build_type = 'release'):
        pass



    def make_install_DAG_by_libDesc(self, libDesc):
        '''
        构建安装依赖图，记录需要安装的节点，已安装节点略过
        每个安装节点可以获取属性:
        configurer, dependent, dependency
        '''
        pass

    def install_by_libDesc_async(self, libDesc):
        groupId, artifactId = parse_libid(libDesc.name)
        pkg = self.get_package(artifactId, groupId)
        config = pkg.get_config()
        installer = pkg.get_installer()
        
        #TODO: auto complete libDesc




    def install_by_configInfo(self, configInfo:InstallConfig):
        groupId, artifactId = parse_libid(configInfo.name)
        pkg = self.get_package(artifactId, groupId)
        config = pkg.get_config()
        installer = pkg.get_installer()

        #auto complete
        host_platform, host_arch = get_sys_info()
        if configInfo.version == None:
            configInfo.version = pkg.get_latest_version()
        if configInfo.platform == None:
            configInfo.platform = host_platform
        if configInfo.arch == None:
            configInfo.arch = host_arch
        if configInfo.build_type == None:
            configInfo.build_type = self.configManager.default_config['build_config']['resource_config']

        config.set_configInfo(configInfo)

        for _ in range(2):
        #尝试安装两遍，第一次安装为了保证configurer依赖正确更新
            dependency = config.get_dependency()
            #check satisfy dependency, if not install dependency
            #TODO

            config.auto_complete()

            #尝试安装
            #TODO

        #尝试人工处理
        if not config.is_legal():
            if not self.solve_config(config):
                raise InstallFailException()
        
        #再次尝试安装
        #TODO

    def install_by_libDesc(self, libDesc:LibDesc):
        pass


    def install_by_libDescs(self, libDescs):
        pass

    def install_by_names(self, names, build_type = 'release'):
        '''
        使用默认设定进行安装
        '''
        pass

    def uninstall_by_name(self, name, build_type = 'release'):
        pass

    def get_package(self, artifactId, groupId = 'main'):
        m = importlib.import_module(f'fxpkg.package.{groupId}.{artifactId}')
        return m.Package(self)

    def add_package(self, src, groupId = 'main', overwrite = True):
        '''
        将package拷贝到对应目录
        若overwrite为False，当目标存在时，会raise PackageAlreadyExists
        '''
        src = Path(src)
        dst = self.pathManager.package_path/groupId
        if not overwrite:
            (dst/src.name).exists()
            raise PackageAlreadyExists()
        if not dst.exists():
            dst.mkdir()
            (dst/'__init__.py').touch()
        src.copy_to(dst, is_prefix=True)

    def solve_config(self, configurer):
        '''
        人工处理，继续尝试安装返回True，否则返回False
        '''
        return False

class ConfigManager:
    def __init__(self, pathManager:PathManager):
        self.pathManager = pathManager
        self.default_config_path = pathManager.root_path/'config/default-config.json'
        self.default_config = self.load_default_config()

    def load_default_config(self):
        self.create_default_config()
        with self.default_config_path.open('r') as fr:
            config = json.load(fr)
        return config
        
    def create_default_config(self):
        if not self.default_config_path.exists():
            (Path(__file__).prnt.prnt/'resource/default-config.json').copy_to(self.default_config_path)