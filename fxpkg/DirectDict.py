class DirectDict:
    def __init__(self, *args, **kwargs):
        super().__setattr__('_data', dict(*args,**kwargs))
    
    def __getattr__(self, x):
        return self._data[x]

    def __setattr__(self,a,v):
        self._data[a] = v

    def get_dict(self):
        return self._data