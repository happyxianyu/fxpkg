from dataclasses import dataclass, asdict

@dataclass
class LibInfoKey:
    name:str
    version:str

    platform:str=""
    arch:str=""
    build_type:str=""

    def to_dict(self):
        return asdict(self)

__all__ = ['LibInfoKey']