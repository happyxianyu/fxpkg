def version_to_tuple(version: str) -> tuple:
    """
    str to tuple
    """
    return tuple(int(x) for x in version.split('.'))


def version_to_str(version: tuple) -> str:
    """
    tuple to str
    """
    return '.'.join(map(str, version))
