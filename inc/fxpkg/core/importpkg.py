import importlib
import fxpkg.package

__all__ = [
    'add_path_to_module',
    'add_package_path',
    'import_package'
]


def add_path_to_module(m, path):
    m.__path__.insert(0, str(path))

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


    