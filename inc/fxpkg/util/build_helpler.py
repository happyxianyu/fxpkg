import logging
import re

from .path import Path
_hook_pattern = re.compile(r"cmake_minimum_required.*\(.*\)")
_stamp = '__fxpkg_dfc839fd-e379-155d-068c-cbeced1dd73c'
_begin_stamp = f'begin {_stamp}'
_end_stamp = f'end {_stamp}'

__all__ = [
    'hook_cmake'
]

def hook_cmake(cmake_file, hook_content:str):
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
        logging.warning(e)
        return False

    with cmake_file.open('w') as fw:
        fw.write(new_content)
    return True