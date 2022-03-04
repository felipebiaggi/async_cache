import base64
import logging
import inspect
import functools
from backend import Resolver
from enums import SerializerType, BackendType

logger = logging.getLogger(__name__)

ENCODE = "UTF-8"


class Cache:
    def __call__(self, func):

        self._cache_instance = Resolver(
            ttl=self.ttl,
            serializer=self.serializer,
            backend=self.backend,
            host=self.host,
            port=self.port,
            pool_size=self.pool_size,
            timeout=self.timeout,
        )

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.create_cache(func, *args, **kwargs)

        return wrapper

    def __init__(
        self,
        ttl=60,
        backend=None,
        host=None,
        port=None,
        timeout=10,
        pool_size=30,
        serializer=SerializerType.PICKLE,
    ):
        self.ttl = ttl
        self.host = host
        self.port = port
        self.backend = backend
        self.timeout = timeout
        self.pool_size = pool_size
        self.serializer = serializer
        self.cache_key = None

        self._cache_instance: Resolver

    async def create_cache(self, func, *args, **kwargs):

        self._create_key(func, args, kwargs)

        value = await self.get_cache(self.cache_key)

        if value is not None:
            logger.debug("Value from cache")
            return value

        func_value = await func(*args, **kwargs)

        await self.set_cache(self.cache_key, func_value)

        logger.debug("Value from function")
        return func_value

    async def get_cache(self, key):
        if self._cache_instance:
            result = await self._cache_instance.get(key)
            return result

    async def set_cache(self, key, value):
        if self._cache_instance:
            result = await self._cache_instance.set(key, value)
            return result

    def _create_key(self, func, args, kwargs):
        params = sorted(kwargs.items())

        default = self.get_default_args(func)

        key = func.__name__ + str(default) + str(args) + str(params)

        self.cache_key = base64.b64encode(key.encode(encoding=ENCODE))

    @staticmethod
    def get_default_args(f):
        signature = inspect.signature(f)
        return {
            k: v.default
            for k, v in signature.parameters.items()
            if v.default is not inspect.Parameter.empty
        }
