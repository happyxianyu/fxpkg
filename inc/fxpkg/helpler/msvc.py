import json
import os
from fxpkg.internal import *

import typing
if typing.TYPE_CHECKING:
    from fxpkg.buildctx import BuildContext


__all__ = [
    'find_vswhere_path',
    'get_msvc_infos'
]



def find_vswhere_path() -> Path:
    msvc_installer_path = Path() / os.environ['ProgramFiles(x86)'] / 'Microsoft Visual Studio/Installer'
    vswhere_path = msvc_installer_path/'vswhere.exe'    # use vswhere.exe to get msvc info
    if vswhere_path.exists():
        return vswhere_path
    else:
        raise FindFailException

async def get_msvc_infos(bctx:'BuildContext'):
    try:
        vswhere_path = find_vswhere_path()
        stdout, stderr = await bctx.run_cmd_async(f'{vswhere_path.quote} -format json -utf8', cwd=vswhere_path.prnt)
        msvc_infos: list = json.loads(stdout)
        return msvc_infos
    except json.JSONDecodeError or FindFailException as e:
        bctx.log.warning(e)
        return []
        




