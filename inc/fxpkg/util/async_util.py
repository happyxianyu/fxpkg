import asyncio
from collections import deque
import tempfile

from fxpkg.util import Path
        

async def run_cmd_async(cmd, cwd = None):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd = cwd
        )

    stdout, stderr = await proc.communicate()
    return stdout, stderr

async def run_shellscript_async(shellscript, tmp_file = None, cwd = None):
    if tmp_file == None:
        tmp_file = tempfile.mkstemp()[1]
    with open(tmp_file,'w') as fw:
        fw.write(shellscript)
    await run_cmd_async(tmp_file, cwd)


async def git_clone_async(self, url, dst, depth = 1):
    if depth == None:
        cmd = f'git clone {url}'
    else:
        cmd = f'git clone --depth={depth} {url}'

    
        

__all__ = [
    'run_cmd_async',
    'run_shellscript_async',
    'git_clone_async'
]