import sqlalchemy as sa
from sqlalchemy import TypeDecorator, BLOB, TEXT
import pickle

from fxpkg.util import Path
class PickleType(TypeDecorator):
    impl = BLOB

    def process_bind_param(self, value, dialect):
        return pickle.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            return pickle.loads(value)

class PathType(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value:str, dialect):
        if value is None:
            return None
        else:
            return Path(value)