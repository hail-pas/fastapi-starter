from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncGenerator
from config.default import InstanceExtensionConfig
from pydantic import RedisDsn

from redis.retry import Retry
from redis.asyncio import Redis, ConnectionPool
from redis.backoff import NoBackoff

class RedisConfig(InstanceExtensionConfig[AsyncGenerator[Redis, None]]):
    url: RedisDsn
    max_connections: int = 10

    @lru_cache()
    def connection_pool(self) -> ConnectionPool:\
        return ConnectionPool.from_url(
                url=str(self.url),
                max_connections=self.max_connections,
                decode_responses=True,
                encoding_errors="strict",
                retry=Retry(NoBackoff(), retries=10),
                health_check_interval=30,
            )


    @asynccontextmanager
    async def instance(self, **kwargs) -> AsyncGenerator[Redis, None]:  # type: ignore
        try:
            r: Redis = Redis(
                connection_pool=self.connection_pool(),
                **kwargs,
            )
            yield r
        finally:
            await r.close()
