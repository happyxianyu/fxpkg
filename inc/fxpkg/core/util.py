import platform

def parse_libid(name):
    '''
    返回(groupId, artifactId)
    '''
    res = name.split('.')
    if len(res) > 1:
        return res[0], ''.join(res[1:])
    else:
        return 'main', name


def get_sys_info():
    '''
    返回(platform, arch)
    '''
    uname = platform.uname()
    return uname.system.lower(), uname.machine.lower()