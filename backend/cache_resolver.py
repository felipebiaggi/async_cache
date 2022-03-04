from backend.base import BackendInterface
from backend.cache_redis import RedisCache
from enums import SerializerType, BackendType
from serializer import PickleSerializer, JsonSerializer
import logging

logger = logging.getLogger(__name__)

backends = {BackendType.REDIS: RedisCache}

serializers = {
    SerializerType.PICKLE: PickleSerializer,
    SerializerType.JSON: JsonSerializer,
}


class Resolver:
    def __init__(
        self,
        ttl=None,
        serializer=None,
        backend=None,
        host=None,
        port=None,
        pool_size=None,
        timeout=10,
    ):
        self._ttl = ttl
        self._host = host
        self._port = port
        self._backend = backend
        self._pool_size = pool_size
        self._serializer = serializer
        self._timeout = timeout

        self.backend_instance: BackendInterface

        _connection_config = {
            "ttl": self._ttl,
            "host": self._host,
            "port": self._port,
            "pool_size": self._pool_size,
            "timeout": self._timeout,
        }

        _cache = backends[self._backend]

        _serializer = serializers[self._serializer]

        self.backend_instance = _cache(**_connection_config)

        self.serializer_instance = _serializer()

    async def get(self, key):
        return self.serializer_instance.loads(await self.backend_instance.get(key))

    async def set(self, key, value):
        return await self.backend_instance.set(
            key, self.serializer_instance.dumps(value)
        )
