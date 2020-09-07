from dataclasses import dataclass
import json

from fxpkg.util import Path

@dataclass
class LibConfig:
    platform:str
    arch:str
    build_type:str

    install_path:str

    other:dict

    @staticmethod
    def load_from_file(path:Path):
        ret = []
        with path.open('r') as f:
            config_list = json.load(f)
        for d in config_list:
            config = LibConfig(**d)
            ret.append(config)
        return ret
    
    @staticmethod
    def get_config_from_list(configs:list, triplet):
        for config in configs:
            if triplet.platform == config.platfom \
                and triplet.arch == config.arch \
                and triplet.build_type == config.build_type:
                return config

    def apply_mask(self, mask:int):
        if not (mask|1):
            self.platform = None
        if not (mask|2):
            self.arch = None
        if not (mask|4):
            self.build_type = None
        

    

__all__ = ['LibConfig']