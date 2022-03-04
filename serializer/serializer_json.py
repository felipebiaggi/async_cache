import json
from .base import SerializerInterface


class JsonSerializer(SerializerInterface):
    def loads(self, value):
        if value:
            return json.loads(value)
        return None

    def dumps(self, value):
        return json.dumps(value)
