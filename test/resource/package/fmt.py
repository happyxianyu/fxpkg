import json
import logging
import pathlib
import re
import traceback
from io import StringIO

from fxpkg import *
from fxpkg.interface import *


class Installer(InstallerBase):
    async def install(self, config: InstallConfig, entry: InstallEntry):
        self.check_support()
        configManager = self.libManager.configManager
        project_path = config.build_path / 'fmt'

        yield 'download'
        git_url = 'https://github.com/fmtlib/fmt.git'
        download_future = self.submit_task(git_clone_async(git_url, config.build_path))

        yield 'configure'
        await download_future
        await self.configure(project_path)

        yield 'build'
        await self.build(project_path)
        self.fill_entry()
        yield 'install'
        await self.final_install(project_path)

    def fill_entry(self):
        entry = self.entry
        entry.lib_list = ['fmt.lib']
        entry.install_state = InstallState.INSTALLING
        logging.debug(entry)

    async def final_install(self, project_path):
        config = self.config
        cmd = f'cmake --build . --target install --config {config.build_type}'
        await self.submit_task(run_cmd_async(cmd, cwd=project_path / '.fxpkg_build'))

    async def build(self, project_path):
        cmd = 'cmake --build .'
        stdout, stderr = await self.submit_task(run_cmd_async(cmd, cwd=project_path / '.fxpkg_build'))

    async def configure(self, project_path):
        await self.write_presets(project_path)
        cmd = 'cmake . -B .fxpkg_build --preset=real'
        await self.submit_task(run_cmd_async(cmd, cwd=project_path))

    async def write_presets(self, project_path):
        cmake_presets = self.make_cmake_presets()
        cmake_presets_path = project_path / 'CMakeUserPresets.json'
        if cmake_presets_path.exists():
            # 更新已存在的配置
            with cmake_presets_path.open('r') as fr:
                cmake_exist_presets: dict = json.loads(fr.read())
                if cmake_presets == cmake_exist_presets:
                    return

                for k,v in cmake_exist_presets.items():
                    if k not in cmake_presets:
                        cmake_presets[k] = v
                config_presets1:list = cmake_presets['configurePresets']
                config_presets1_names = {x['name'] for x in config_presets1}
                config_presets2:list = cmake_exist_presets.get('configurePresets')
                if config_presets2 is not None:
                    name_set = config_presets1_names-{'real'}
                    for p2 in config_presets2:
                        if p2['name'] not in name_set:
                            config_presets1.append(p2)
        with cmake_presets_path.open('w') as fw:
            json.dump(cmake_presets, fw)

    def get_generator_name(self):
        config = self.config
        msvc_tool = next((x for x in config.toolset if x['name'] == 'msvc'), None)
        print(msvc_tool)
        msvc_generator_map = {
            '2019': 'Visual Studio 16 2019'
        }

        generator_name = msvc_generator_map[msvc_tool['line_version']]
        return generator_name

    def make_cmake_presets(self) -> dict:
        config = self.config
        generator_name = self.get_generator_name()
        cmake_presets = {
            'version': 2,
            'configurePresets': [
                {
                    'name': 'real',  # 最终使用的
                    'inherits': 'default',
                },
                {
                    'name': 'default',
                    'generator': generator_name,
                    "binaryDir": '.fxpkg_build_binary',
                    'cacheVariables': {
                        'CMAKE_INSTALL_PREFIX': {
                            'value': str(config.install_path)
                        },
                        'CMAKE_PREFIX_PATH': {
                            'value': str(config.install_path)
                        },
                    },
                },
            ]
        }
        return cmake_presets

    def check_support(self):
        try:
            config = self.config
            configManager = self.libManager.configManager
            assert configManager.host_arch == config.arch
            assert configManager.host_platform == config.platform
            # 不支持交叉编译，要求全部和宿主平台一致
            if configManager.host_platform == 'windows':
                # 对于windows平台，只支持使用msvc
                assert config.compiler == 'cl'
        except AssertionError as e:
            raise NotSupportError(self.exception_to_str(e))

    @staticmethod
    def exception_to_str(e: Exception):
        return traceback.format_tb(e.__traceback__)[0]


class Package(PackageBase):
    def __init__(self, libManager: LibManager):
        super().__init__(libManager)
        logging.debug('load fmt')

    def get_versions(self):
        return ['7.1.3']

    def make_installer(self) -> InstallerBase:
        return Installer(self.libManager)
