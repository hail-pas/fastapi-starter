import enum
from urllib.parse import unquote
from config.default import RegisterExtensionConfig
from pydantic import MySQLDsn
from tortoise import Tortoise

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
                        "storages.relational.models.user_center",
                    ],
                    "default_connection": ConnectionNameEnum.user_center.value,
                },
                ConnectionNameEnum.second.value: {
                    "models": [
                        "storages.relational.models.second",
                    ],
                    "default_connection": ConnectionNameEnum.second.value,
                },
            },
            # "use_tz": True,   # Will Always Use UTC as Default Timezone
            "timezone": self.timezone,
            # 'routers': ['path.router1', 'path.router2'],
        }


    def register(self, **kwargs):
        Tortoise.init(config=self.to_dict())
