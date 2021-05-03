import asyncio
import logging

from fxpkg.util.async_util import *
from fxpkg import Path

print = logging.debug

self_path = Path(__file__)
prnt_path = self_path.prnt
test_path = prnt_path / 'tmp/test_async_util'


def test_git_clone():
    url = 'https://github.com/fmtlib/fmt.git'

    async def impl():
        result = await git_clone_async(url, test_path)
        print(result)

    asyncio.run(impl())
