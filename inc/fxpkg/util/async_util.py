import asyncio
from collections import deque
import tempfile
import logging

from fxpkg.util import Path
        

__all__ = ['run_cmd_async',
           'run_shellscript_async',
           'git_clone_async']

async def run_cmd_async(cmd, cwd = None):
    if cwd is not None:
        Path(cwd).mkdir()
        cwd = str(cwd)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd = cwd
        )

    stdout, stderr = await proc.communicate()
    return stdout, stderr

async def run_shellscript_async(shellscript:str , tmp_file = None, cwd = None):
    if tmp_file == None:
        tmp_file = tempfile.mkstemp()[1]
    tmp_file_path = Path(tmp_file)
    with tmp_file_path.open('w') as fw:
        fw.write(shellscript)

    cmd = f'{tmp_file_path.escape_str}'
    return await run_cmd_async(tmp_file, cwd)

async def git_clone_async(url, cwd, dst = None, depth = None):
    dst = str(dst)
    if depth == None:
        cmd = f'git clone {url} {dst}'
    else:
        cmd = f'git clone --depth={depth} {url} {dst}'
    return await run_cmd_async(cmd, cwd=cwd)
    
        

__all__ = [
    'run_cmd_async',
    'run_shellscript_async',
    'git_clone_async'
]