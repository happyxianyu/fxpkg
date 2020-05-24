def all_(*args):
    return ('all', *args)

def any_(*args):
    return ('any', *args)

def optional(x):
    return ('opt', x)

opt = optional