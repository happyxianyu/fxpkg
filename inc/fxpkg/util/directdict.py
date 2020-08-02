class DirectDict:
    def __new__(cls, *args, **kwargs):
        ret = super().__new__(cls)
        super(DirectDict, ret).__setattr__('_data', dict()) 
        return ret

    def __init__(self, *args, **kwargs):
        pass
        # super().__setattr__('_data', dict(*args,**kwargs)) 

    def __getattr__(self, k):
        return self._data[k]

    def __setattr__(self,k,v):
        self._data[k] = v

    def get_dict(self):
        return self._data

    def to_str(self, f = str):
        return f(self.get_dict())
    
    def __str__(self):
        return self.to_str(str)

    def __repr__(self):
        return self.to_str(repr)