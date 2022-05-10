import re
from fxpkg.internal import *
from fxpkg.common import *

__all__=[
    'get_msvc_cmake_generator',
    'get_cmake_generator',
    'make_cmake_presets',
    'hook_cmake'
]


def get_msvc_cmake_generator(msvc_info:dict):
    year2gen={
        '2019' : 'Visual Studio 16 2019',
        '2017' : 'Visual Studio 15 2017',
        '2015' : 'Visual Studio 14 2015',
        '2013' : 'Visual Studio 12 2013',
        '2012' : 'Visual Studio 11 2012',
        '2010' : 'Visual Studio 10 2010',
        '2008' : 'Visual Studio 9 2008',
    }
    year = msvc_info['catalog']['productLineVersion']
    return year2gen[year]



def get_cmake_generator(config:InstallConfig):
    msvc_infos = config.toolset.msvc_infos
    if len(msvc_infos):
        msvc_info = config.toolset.choose_msvc()
        return get_msvc_cmake_generator(msvc_info)




def make_cmake_presets(config:InstallConfig, install_path=None) -> dict:
    if install_path is None:
        install_path = config.install_path
    cmake_generator = config.cmake.generator
    cmake_presets = {
        'version': 2,
        'configurePresets': [
            {
                'name': 'real',  # 最终使用的
                'inherits': 'default',
            },
            {
                'name': 'default',
                'generator': cmake_generator,
                "binaryDir": '.fxpkg/binary',
                'cacheVariables': {
                    'CMAKE_INSTALL_PREFIX': {
                        'value': str(install_path)
                    },
                    'CMAKE_PREFIX_PATH': {
                        'value': str(install_path)
                    },
                },
            },
        ]
    }
    return cmake_presets




_hook_pattern = re.compile(r"cmake_minimum_required.*\(.*\)")
_stamp = '__fxpkg_dfc839fd-e379-155d-068c-cbeced1dd73c'
_begin_stamp = f'begin {_stamp}'
_end_stamp = f'end {_stamp}'


def hook_cmake(bctx:'BuildContext', cmake_file, hook_content:str):
    log = bctx.log
    cmake_file = Path(cmake_file)
    with cmake_file.open('r') as fr:
        content = fr.read()
    real_hook_content = \
f'''# {_begin_stamp}
{hook_content}
# {_end_stamp}'''

    hook_pos = content.find('# ' + _begin_stamp)
    try:
        if hook_pos != -1:
            hook_endpos = content.find(_end_stamp) + len(_end_stamp)
            new_content = content[:hook_pos] + real_hook_content + content[hook_endpos:]
        else:
            matched = _hook_pattern.search(content)
            hook_pos = matched.span()[1]
            new_content = content[:hook_pos] + real_hook_content + content[hook_pos:]
    except Exception as e:
        log.warning(e)
        return False

    with cmake_file.open('w') as fw:
        fw.write(new_content)
    return True