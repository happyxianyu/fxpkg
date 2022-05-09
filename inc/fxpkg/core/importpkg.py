from cbutil import Path
import typing
import importlib
from fxpkg.util import Path
import fxpkg.package

if typing.TYPE_CHECKING:
    from fxpkg import BuildContext

__all__ = [
    'add_path_to_module',
    'add_package_path',
    'import_package',
    'get_package_mgr',
    'find_submodules'
]


def add_path_to_module(m, path):
    m.__path__.insert(0, str(path))

def is_path_py_module(path):
    path = Path(path)
    if path.ext == 'py':
        return True
    if not path.exists() or path.is_file():
        return False
    return any(f.name == '__init__.py' for f in path.file_son_iter)

    

def find_submodules(m) -> typing.Set[Path]:
    modules = set()
    paths = m.__path__
    for path in paths:
        path = Path(path)
        for p in path.son_iter:
            if is_path_py_module(p):
                modules.add(p)
    return modules


def add_package_path(path):
    """
    Add a package manager modules path
    """
    add_path_to_module(fxpkg.package, str(path))

def import_package(name):
    """
    import a package manager module from package manager modules paths
    """
    return importlib.import_module(f'fxpkg.package.{name}')

def get_package_mgr(bctx:'BuildContext', libid:str):
    return import_package(libid).get_package_mgr(bctx)


def find_package_mgrs():
    return find_submodules(fxpkg.package)
    

