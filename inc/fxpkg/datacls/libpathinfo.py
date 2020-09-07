from dataclasses import dataclass
import dataclasses as dc

from fxpkg.util import Path

@dataclass
class LibPathInfo:
    config:Path
    download:Path
    src:Path
    build:Path
    install:Path
    data:Path
    log:Path
    cache:Path
    tmp:Path

    def make_sub_info(self, subname:str):
        return LibPathInfo(**{k:v/subname for k,v in dc.asdict(self).items()})

    def create(self):
        for a in LibPathInfo.attrs:
            v = getattr(self, a)
            v.mkdir()

LibPathInfo.attrs = [f.name for f in dc.fields(LibPathInfo)]

__all__ = ['LibPathInfo']