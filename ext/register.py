from pydantic import BaseModel

from ext.ext_oss.main import OssConfig
from ext.ext_redis.main import RedisConfig
from ext.ext_tortoise.main import TortoiseConfig


class ExtensionRegistry(BaseModel):
    """
    define here
    """

    redis: RedisConfig
    oss: OssConfig
    # relation: TortoiseConfig
    rdb_user_center: TortoiseConfig
    rdb_second: TortoiseConfig
