from mylib import Path
from pprint import pprint
import json
import sys

from libinfo_lib import *

self_path =Path( sys.path[0])
cpp_root = Path(r'D:\Bill\code\cpp')
src_root = cpp_root/'src'
inst_root = cpp_root/'installed'

not_lib_src_dirs = get_line_strip( r'''
myproject
mytest
sample
zipped-packages
''')

lib_names = get_line_strip( r'''
boost
double-conversion
eigen
fmt
folly
gflags
glog
glut
libevent
libnoise
DirectXTK
DXUT
FX11
'''
)


def insert_table():
    src_paths = list(src_root.get_dir_son_iter(lambda x: x.name not in not_lib_src_dirs))

    def find_src_paths():
        src_paths_d = dict()
        src_path_names = [p.name for p in src_paths]
        unsure_list = []
        for name in lib_names:
            i,r = find_closet_str(name, src_path_names)
            src_paths_d[name] = src_paths[i]
            if r<80: unsure_list.append([r,name,src_paths[i] ])

        print('find src paths:')
        pprint(src_paths_d)
        print('\n')
        if len(unsure_list):
            print('unsure: ')
            pprint(unsure_list)
            print('\n')
        return src_paths_d
            
    src_paths_d = find_src_paths()


    #begin generate
    repo = LibInfoRepo(debug = True, reinit= True)

    rel_paths_dict = dict(
        inc_path = 'include',
        lib_path = 'lib',
        bin_path = 'bin',
        cmake_path = 'cmake',
    )

    proc_list = []
    register_proc = lambda f: proc_list.append(f)
    regp = register_proc


    @regp
    def _():
        boost_root = inst_root/'boost'
        key = dict(name = 'boost', arch = 'x64', platform = 'windows', build_type = ['debug','release'])
        val = dict(
            src_path = src_paths_d['boost'],
            inc_path = boost_root/'include'/'boost-1_73',
            lib_path = boost_root/'lib', 
            cmake_path = boost_root/'cmake')
        repo.update(key,val)

    for proc in proc_list:
        proc()

insert_table()