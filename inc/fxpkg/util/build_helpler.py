import re

from .path import Path
_hook_pattern = re.compile(r'check_minimum_required.*\(.*\)')

def hook_cmake(cmake_file, module_name:str):
    cmake_file = Path(cmake_file)
    with cmake_file.open('r') as fr:
        content = fr.read()
    hook_content = f'''
    
    include({module_name})
    
    '''
    matched = _hook_pattern.search(content)

    hook_pos = matched.endpos
    new_content = content[:hook_pos] + hook_content + content[hook_pos:]

    with cmake_file.open('w') as fw:
        fw.write(new_content)