from dataclasses import dataclass

@dataclass
class LibConfig:
    version:str

    platform:str
    arch:str
    build_type:str

    install_path:str

    other:dict