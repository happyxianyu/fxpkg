
class VersionSetBase:
    def __contains__(self, ver):
        return False

    def __iter__(self):
        '''
        返回可用版本，不一定要全面
        '''
        return iter()