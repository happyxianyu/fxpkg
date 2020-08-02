import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

# from fxpkg.util import DirectDict
metadata = MetaData()
# Base = declarative_base(metadata=metadata, cls=DirectDict)
Base = declarative_base(metadata=metadata)

__all__ = ['metadata', 'Base']