from fxpkg.util import Path
import fxpkg.common.config as cfg


cfg.path_info

if vs_root:=cfg.path_info['visual_studio_root']:
    class MSVS:
        root = vs_root
        
        @staticmethod
        def get_build_path(year = '2019', version = 'Enterprise'):
            return MSVS.root/year/version/r'VC/Auxiliary/Build'