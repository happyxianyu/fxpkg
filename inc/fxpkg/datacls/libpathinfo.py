from dataclasses import dataclass
import dataclasses as dc

from fxpkg.util import Path

@dataclass
class LibPathInfo:
    config:Path
    cache:Path
    install:Path
    data:Path
    log:Path
    tmp:Path

    def make_sub_info(self, subname:str):
        return LibPathInfo(**{k:v/subname for k,v in dc.asdict(self).items()})

LibPathInfo.attrs = [f.name for f in dc.fields(LibPathInfo)]

__all__ = ['LibPathInfo']