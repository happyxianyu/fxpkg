import sys
from cbutil import load_module, Path

tmp_path = Path(r'D:\temp')
main_path = tmp_path/'main.py'

m = load_module(main_path)
print(m)

m.foo()