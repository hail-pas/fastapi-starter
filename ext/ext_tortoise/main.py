import enum
import datetime
from typing import override
from zoneinfo import ZoneInfo
from urllib.parse import unquote

from fastapi import FastAPI
from pydantic import MySQLDsn
from tortoise import Tortoise

from config.default import RegisterExtensionConfig


class ConnectionNameEnum(str, enum.Enum):
    """数据库连接名称"""

    # default = "default"  # "默认连接"
    user_center = "user_center"  # "用户中心连接"
    second = "second"


class TortoiseConfig(RegisterExtensionConfig):
    user_center: MySQLDsn
    second: MySQLDsn
    timezone: str = "Asia/Shanghai"
    echo: bool = False

    # model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def datetime_now(self) -> datetime.datetime:
        return datetime.datetime.now(
            tz=ZoneInfo(self.timezone),
        )

    def to_dict(self) -> dict:
        return {
            "connections": {
                ConnectionNameEnum.user_center.value: {
                    # "engine": "tortoise.backends.sqlite",
                    # "credentials": {"file_path": ":memory:"},
                    "engine": "tortoise.backends.mysql",
                    "credentials": {
                        "host": self.user_center.host,
                        "port": self.user_center.port,
                        "user": self.user_center.username,
                        "password": unquote(self.user_center.password) if self.user_center.password else "",
                        "database": self.user_center.path.strip("/"),  # type: ignore
                        "echo": self.echo,
                        "minsize": 1,  # 连接池的最小连接数
                        "maxsize": 10,  # 连接池的最大连接数
                        "pool_recycle": 3600,  # 连接的最大存活时间（秒）
                    },
                },
                ConnectionNameEnum.second.value: {
                    # "engine": "tortoise.backends.sqlite",
                    # "credentials": {"file_path": ":memory:"},
                    "engine": "tortoise.backends.mysql",
                    "credentials": {
                        "host": self.second.host,
                        "port": self.second.port,
                        "user": self.second.username,
                        "password": unquote(self.second.password) if self.second.password else "",
                        "database": self.second.path.strip("/"),  # type: ignore
                        "echo": self.echo,
                        "minsize": 1,  # 连接池的最小连接数
                        "maxsize": 10,  # 连接池的最大连接数
                        "pool_recycle": 3600,  # 连接的最大存活时间（秒）
                    },
                },
            },
            "apps": {
                ConnectionNameEnum.user_center.value: {
                    "models": [
                        "aerich.models",
                        "ext.ext_tortoise.models.user_center",
                    ],
                    "default_connection": ConnectionNameEnum.user_center.value,
                },
                ConnectionNameEnum.second.value: {
                    "models": [
                        "ext.ext_tortoise.models.second",
                    ],
                    "default_connection": ConnectionNameEnum.second.value,
                },
            },
            # "use_tz": True,   # Will Always Use UTC as Default Timezone
            "timezone": self.timezone,
            # 'routers': ['path.router1', 'path.router2'],
        }

    @override
    async def register(self) -> None:
        Tortoise.init_models(
            [
                "ext.ext_tortoise.models.user_center",
            ],
            ConnectionNameEnum.user_center.value,
        )

        Tortoise.init_models(
            [
                "ext.ext_tortoise.models.second",
            ],
            ConnectionNameEnum.second.value,
        )
        await Tortoise.init(config=self.to_dict())

    @override
    async def unregister(self) -> None:
        await Tortoise.close_connections()
