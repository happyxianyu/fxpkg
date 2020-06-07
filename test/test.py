from cbutil import Path
tmp_path = Path(r'D:\temp')


# from fxpkg import init_fxpkg_root
# root_path = tmp_path/'pkg_root'
# init_fxpkg_root(root_path)


import sys

(tmp_path/'a.txt').copy_to(tmp_path/'b')
