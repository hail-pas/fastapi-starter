from enum import unique

from etype.enum import StrEnum


@unique
class RequestHeaderKeyEnum(StrEnum):
    """请求头key"""

    front_scene = ("X-Front-Scene", "请求的系统标识")
    front_version = ("X-Front-Version", "版本号")
