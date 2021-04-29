import sqlalchemy as sa
from sqlalchemy import TypeDecorator, BLOB
import pickle

class PickleType(TypeDecorator):
    impl = BLOB

    def process_bind_param(self, value, dialect):
        return pickle.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            return pickle.loads(value)