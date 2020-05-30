from .path import Path

self_path = Path(__file__)

def init_pkg_root(root_path):
    src_root_path = self_path.prnt/'pkg_root'
    dst_root_path = Path(root_path)
    src_root_path.copy_sons_to(dst_root_path)
    