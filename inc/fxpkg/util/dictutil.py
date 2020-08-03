def update_attr(dst: object, src: dict, cond=None):
    '''
    update if cond(k) == True or cond is None
    '''
    for k, v in src.items():
        if (cond is None) or cond(k):
            setattr(dst, k, v)


def update_attr1(dst: object, src: dict):
    '''
    update if not hasattr
    '''
    for k, v in src.items():
        if not hasattr(dst, k):
            setattr(dst, k, v)


def update_attr2(dst: object, src: dict):
    '''
    update if not hasattr or is none
    '''
    for k, v in src.items():
        if not hasattr(dst, k):
            setattr(dst, k, v)
        else:
            v = getattr(dst, k)
            if v is None:
                setattr(dst, k, v)

def update_dict(dst: dict, src: dict, cond=None):
    '''
    update if cond(k) == True 
    or cond is None
    '''
    for k, v in src.items():
        if (cond is None) or cond(k):
            setattr(dst, k, v)

def update_dict1(dst: dict, src: dict):
    '''
    update if dst does not has key
    '''
    for k, v in src.items():
        if k not in dst:
            dst[k] = src[k]

def update_dict2(dst: dict, src: dict):
    '''
    update if dst does not has key 
    or if value is None
    '''
    for k, v in src.items():
        v = dst.get(k)
        if v is None:
            dst[k] = src[k]