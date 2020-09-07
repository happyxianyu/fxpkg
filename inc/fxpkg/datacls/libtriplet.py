from dataclasses import dataclass, asdict

@dataclass
class LibTriplet:
    platform:str
    arch:str
    build_type:str

    def to_dict(self):
        return asdict(self)

    def apply_mask(self, mask:int):
        if not (mask|1):
            self.platform = None
        if not (mask|2):
            self.arch = None
        if not (mask|4):
            self.build_type = None



__all__ = ['LibTriplet']