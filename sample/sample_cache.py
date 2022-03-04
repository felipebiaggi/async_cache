import asyncio
import pprint
from cache import Cache
from enums import SerializerType, BackendType


@Cache(
    ttl=60,
    serializer=SerializerType.PICKLE,
    backend=BackendType.REDIS,
    host="localhost",
    port=6379,
    pool_size=30,
)
async def func(foo=None, bar=None):
    return f"Result: FOO <{foo}> --- BAR <{bar}>"


async def main():
    result = await func(foo="TESTE", bar=10000)
    pprint.pprint(result)


if __name__ == "__main__":
    asyncio.run(main())
