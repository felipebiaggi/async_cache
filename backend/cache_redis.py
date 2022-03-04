import logging
import asyncio
import aioredis
import functools
from backend.base import BackendInterface

logger = logging.getLogger(__name__)


def func_timeout(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        if self._timeout:
            return await asyncio.wait_for(
                func(self, *args, **kwargs), timeout=self._timeout
            )
        return await func(self, *args, **kwargs)

    return wrapper


class RedisCache(BackendInterface):
    def __init__(
        self, host="localhost", port=6379, pool_size=10, database=0, ttl=60, timeout=10
    ):
        self._ttl = ttl
        self._host = host
        self._port = port
        self._timeout = timeout
        self._database = database
        self._pool_size = pool_size

        self._pool = None
        self.__pool_lock = None

    @property
    def _pool_lock(self):
        """from https://github.com/aio-libs/aiocache/blob/master/aiocache/backends/redis.py#L81"""
        if self.__pool_lock is None:
            self.__pool_lock = asyncio.Lock()
        return self.__pool_lock

    async def connection(self):
        await self.create_connection()
        return aioredis.Redis(connection_pool=self._pool)

    @func_timeout
    async def get(self, key, *args):
        redis = await self.connection()

        async with redis.client() as conn:
            return await conn.get(key)

    @func_timeout
    async def set(self, key, value, *args):
        redis = await self.connection()

        async with redis.client() as conn:
            return await conn.set(key, value, ex=self._ttl)

    async def create_connection(self):
        async with self._pool_lock:
            if self._pool is None:
                self._pool = aioredis.ConnectionPool.from_url(
                    url=f"redis://{self._host}:{self._port}",
                    encoding="utf-8",
                )
            return self._pool
