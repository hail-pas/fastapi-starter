import asyncio
from asyncio import subprocess
import enum
import datetime
from typing import AsyncGenerator, override
from zoneinfo import ZoneInfo
from functools import cached_property
from contextlib import asynccontextmanager

from alembic import command
from pydantic import MySQLDsn
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.util import greenlet_spawn

from config.default import BASE_DIR, InstanceExtensionConfig, RegisterExtensionConfig


class ConnectionNameEnum(str, enum.Enum):
    """数据库连接名称"""

    # default = "default"  # "默认连接"
    user_center = "user_center"  # "用户中心连接"
    second = "second"


class SqlModelConfig(InstanceExtensionConfig[AsyncSession], RegisterExtensionConfig):
    url: MySQLDsn
    echo: bool = False

    # model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def datetime_now(self) -> datetime.datetime:
        from config.main import local_configs
        return datetime.datetime.now(
            tz=ZoneInfo(local_configs.server.timezone),
        )

    @override
    async def register(self) -> None:
        # 直接使用代码无法执行成功
        # alembic_cfg = Config(
        #     f"{BASE_DIR}/ext/ext_sqlmodel/alembic.ini",
        #     attributes={"script_location": f"{BASE_DIR}/ext/ext_sqlmodel/migration"},
        # )
        # command.upgrade(alembic_cfg, "head")
        # 重复执行会有问题
        # await subprocess.create_subprocess_shell(f"alembic --config {BASE_DIR}/ext/ext_sqlmodel/alembic.ini upgrade head")
        pass

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
