class SerializerInterface:
    def loads(self, value):
        raise NotImplementedError()

    def dumps(self, value):
        raise NotImplementedError()
