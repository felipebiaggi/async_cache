class BackendInterface:
    async def get(self, key):
        raise NotImplementedError()

    async def set(self, key, value):
        raise NotImplementedError()
