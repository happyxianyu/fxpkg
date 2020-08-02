import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)

__all__ = ['metadata', 'Base']