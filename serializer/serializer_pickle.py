import pickle
from .base import SerializerInterface


class PickleSerializer(SerializerInterface):
    def loads(self, value):
        if value:
            return pickle.loads(value)
        return None

    def dumps(self, value):
        return pickle.dumps(value)
