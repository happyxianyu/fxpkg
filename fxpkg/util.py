from collections import namedtuple
from itertools import product as cart_prod
import re
from fuzzywuzzy.fuzz import WRatio as fuzzy_ratio



#begin str util
def remove_empty_str(l:list):
    return [s for s in l if s!=None and s.strip() != '']

def remove_none_item(d:dict):
    return {k:v for k,v in d.items() if v!=None}

    
def split_strip(s:str, spl:str):
    return remove_empty_str(s.split(spl))

def get_words(s:str):
    return re.findall(r'\S+',s)

def get_line_strip(s:str):
    return split_strip(s,'\n')

def find_closet_str(dst:str, srcs:list):
    '''
    return (index, ratio)

    example:
    index,ratio = find_closet_str('apple', ['banna', 'grape', 'apple'])
    '''
    idx = -1
    r = -1
    for i,src in enumerate(srcs):
        r1 = fuzzy_ratio(dst,src)
        if r1>r:
            idx = i
            r = r1
    return idx, r
#end str util




def to_namedtuple(x:dict, name = 'NamedTuple'):
    return namedtuple(name, x.keys())(**x)

def canonicalize_to_tuple(x):
    return ((x,),x) [type(x) in (list,tuple)]
ctt = canonicalize_to_tuple

def cart_prod_dict(d:dict) -> list:
    d = {k:ctt(v) for k,v in d.items()}
    keys = []
    vals = []
    for k,v in d.items():
        keys.append(k)
        vals.append(v)
    vals1 = tuple(cart_prod(*vals))
    return [{k:v for k,v in zip(keys,vals1[i])} for i in range(len(vals1))] 

