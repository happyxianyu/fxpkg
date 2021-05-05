import asyncio
from collections import deque
import tempfile
import logging
import aiofile

from fxpkg.util import Path

__all__ = ['run_cmd_async',
           'run_shellscript_async',
           'git_clone_async']


async def run_cmd_async(cmd, cwd=None, env=None):
    if cwd is not None:
        Path(cwd).mkdir()
        cwd = str(cwd)

    if env is not None:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env
        )
    else:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

    stdout, stderr = await proc.communicate()
    return stdout, stderr


async def run_shellscript_async(shellscript: str, tmp_file=None, cwd=None, env=None):
    if tmp_file == None:
        tmp_file = tempfile.mkstemp(suffix='.bat')[1]
    tmp_file_path = Path(tmp_file)
    if not tmp_file_path.exists():
        tmp_file_path.touch()

    async with aiofile.AIOFile(tmp_file_path, 'w') as fw:
        await fw.write(shellscript)

    cmd = f'{tmp_file_path.quote()}'
    return await run_cmd_async(cmd, cwd, env)


async def git_clone_async(url, cwd, dst='', depth=None):
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
