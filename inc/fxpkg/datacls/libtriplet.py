from dataclasses import dataclass

@dataclass
class LibTriplet:
    platform:str
    arch:str
    build_type:str

__all__ = ['LibTriplet']