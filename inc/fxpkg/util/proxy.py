class DictObjectPorxy:
    def __init__(self, o:object):
        self.o = o

    def keys(self):
        return dir(self.o)

    def items(self):
        for k in self.keys():
            yield getattr(self.o, k)

    def __getitem__(self, key):
        return getattr(self.o, key)

    def __setitem__(self, key, value):
        setattr(self.o, key, value)

    def __delitem__(self, key):
        delattr(self.o, key)

    def __contains__(self, key):
        return hasattr(self.o, key)

    def replace(self, d:dict):
        for k in d:
            self[k] = d
