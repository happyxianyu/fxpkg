import json
import logging
import pathlib
import re

from fxpkg import *


class Installer(InstallerBase):
    async def install(self, config: InstallConfig, entry: InstallEntry):
        configManager = self.libManager.configManager
        print(entry)
        # 不支持交叉编译，要求全部和宿主平台一致
        assert configManager.host_arch == config.arch
        assert configManager.host_platform == config.platform
        if configManager.host_platform == 'windows':
            #对于windows平台，只支持使用msvc
            assert config.compiler == 'cl'
        project_path = config.build_path / 'fmt'

        yield 'download'
        git_url = 'https://github.com/fmtlib/fmt.git'
        future = self.submit_task(git_clone_async(git_url, config.build_path))
        yield 'configure'
        cmake_presets = self.make_cmake_presets()

        print(project_path)
        await future
        cmake_presets_path = project_path / 'CMakeUserPresets.json'
        with cmake_presets_path.open('w') as fw:
            json.dump(cmake_presets, fw)

        cmd = 'cmake . -B .fxpkg_build --preset=default'
        await self.submit_task(run_cmd_async(cmd, cwd=project_path))
        yield 'build'
        cmd = 'cmake --build .'
        stdout, stderr = await self.submit_task(run_cmd_async(cmd, cwd=project_path/'.fxpkg_build'))
        yield 'install'
        entry.install_state = InstallState.INSTALLING
        cmd = f'cmake --build . --target install --config {config.build_type}'
        await self.submit_task(run_cmd_async(cmd, cwd=project_path/'.fxpkg_build'))
        entry.install_state = InstallState.INTACT

    def get_generator_name(self):
        config = self.config
        msvc_tool = next((x for x in config.toolset if x['name'] == 'msvc'), None)
        print(msvc_tool)
        msvc_generator_map = {
            '2019': 'Visual Studio 16 2019'
        }

        generator_name = msvc_generator_map[msvc_tool['line_version']]
        return generator_name

    def make_cmake_presets(self):
        config = self.config
        generator_name = self.get_generator_name()
        cmake_presets = {
            'version': 2,
            'configurePresets': [
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
                }
            ]
        }


class Package(PackageBase):
    def __init__(self, libManager: LibManager):
        super().__init__(libManager)
        logging.debug('load fmt')

    def get_versions(self):
        return ['7.1.3']

    def make_installer(self) -> InstallerBase:
        return Installer(self.libManager)
