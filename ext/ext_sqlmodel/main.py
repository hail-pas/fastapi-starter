import enum
import datetime
from typing import AsyncGenerator, override
from zoneinfo import ZoneInfo
from functools import cached_property
from contextlib import asynccontextmanager

from pydantic import MySQLDsn
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.default import InstanceExtensionConfig, RegisterExtensionConfig


class ConnectionNameEnum(str, enum.Enum):
    """数据库连接名称"""

    # default = "default"  # "默认连接"
    user_center = "user_center"  # "用户中心连接"
    second = "second"


class SqlModelConfig(InstanceExtensionConfig[AsyncSession], RegisterExtensionConfig):
    url: MySQLDsn
    timezone: str = "Asia/Shanghai"
    echo: bool = True

    # model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def datetime_now(self) -> datetime.datetime:
        return datetime.datetime.now(
            tz=ZoneInfo(self.timezone),
        )

    @override
    async def register(self) -> None: ...

    @override
    async def unregister(self) -> None: ...

    @property
    @asynccontextmanager
    @override
    async def instance(self) -> AsyncGenerator[AsyncSession, None]:  # type: ignore
        s: AsyncSession | None = None
        try:
            s = self.sessionmaker()
            yield s  # type: ignore
        finally:
            if s:
                await s.close()

    @cached_property
    def engine(self) -> AsyncEngine:
        return create_async_engine(
            str(self.url),
            echo=self.echo,
            future=True,
            pool_size=10,
        )

    @cached_property
    def sessionmaker(self) -> async_sessionmaker:
        return async_sessionmaker(bind=self.engine, expire_on_commit=False)
