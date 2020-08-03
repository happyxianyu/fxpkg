class FxConfig:
    def __init__(self, **kwargs):
        attrs = list()
        super().__setattr__('__config_attrs_', attrs)
        for k,v in kwargs.items():
            super().__setattr__(k, v)
            attrs.append(k)
        
    def __setattr__(self, k, v):
        if not hasattr(self, k):
            self.get_attrs().append(k)
        super().__setattr__(k, v)
    
    def __delattr__(self, k):
        super().__delattr__(k)
        attrs = self.get_attrs()
        del attrs[attrs.index(k)]

    def get_attrs(self) -> list:
        return super().__getattribute__('__config_attrs_')

    def to_dict(self):
        ret = {}
        for k in self.get_attrs():
            ret[k] = getattr(self, k)
        return ret

    def to_str(self, ts = str):
        attrs = self.get_attrs()
        l = ['{']
        for a in attrs:
            v = ts(getattr(self, a))
            l.append(f'{a}: {v};')
        l.append('}')
        return  '\n'.join(l) 
    
    def __repr__(self):
        return self.to_str(repr)
    
    def __str__(self):
        return self.to_str(str)
        