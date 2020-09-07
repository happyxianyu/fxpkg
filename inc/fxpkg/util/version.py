class Version:
    def __init__(self, ver):
        if type(ver) == str:
            data =[int(x) for x in ver.split('.')]
        elif type(ver) == Version:
            data = ver.data.copy()
        else:
            raise TypeError(type(data))
        self.data:list = data

    def cmp(self, ver):
        d1,d2 = self.data, ver.data
        for x1,x2 in d1,d2:
            if x1<x2:
                return -1
            elif x1>x2:
                return 1
        return 0

    def __str__(self):
        return '.'.join(self.data)

    def __repr__(self):
        return str(self)
        
    @property
    def str(self):
        return str(self)


class VersionInterval:
    def __init__(self, a=None, b=None):
        if a is None:
            self.a = None
        else:
            self.a:Version = Version(a)
        if b is None:
            self.b = None
        else:
            self.b:Version = Version(b)

    def __contains__(self, x:Version):
        a,b = self.a, self.b
        if not (a and a.cmp(x) < 1):
            return False
        if not (b and x.cmp(b) < 1):
            return False
        return True
            