import time
import uuid
from enum import unique

from loguru import logger
from starlette.types import Message
from starlette_context import context
from starlette.requests import Request, HTTPConnection
from starlette.responses import Response
from starlette.datastructures import MutableHeaders
from starlette_context.plugins import Plugin

from etype.enum import StrEnum
from core.response import ResponseCodeEnum


@unique
class ContextKeyEnum(StrEnum):
    """上下文变量key."""

    # plugins
    request_id = ("request_id", "请求ID")
    request_start_timestamp = ("request_start_timestamp", "请求开始时间")
    request_body = ("request_body", "请求体")
    process_time = ("process_time", "请求处理时间/ms")

    # custom
    response_code = ("response_code", "响应code")
    response_data = ("response_data", "响应数据")  #  只记录code != 0 的


@unique
class ResponseHeaderKeyEnum(StrEnum):
    """响应头key"""

    request_id = ("X-Request-Id", "请求唯一ID")
    process_time = ("X-Process-Time", "请求处理时间")  # ms


# enrich response 会触发两次 http.response.start、http.response.body
class RequestIdPlugin(Plugin):
    """请求唯一标识"""

    key: str = ContextKeyEnum.request_id.value
    # is_internal: bool = False

    # def __init__(self, is_internal: bool = False) -> None:
    #     self.is_internal = is_internal

    async def process_request(
        self,
        request: Request | HTTPConnection,
    ) -> str:
        # if self.is_internal:
        request_id = request.headers.get(
            ResponseHeaderKeyEnum.request_id.value,
        )
        return request_id or str(uuid.uuid4())

    async def enrich_response(
        self,
        response: Response | Message,
    ) -> None:
        value = str(context.get(self.key))
        # for ContextMiddleware
        if isinstance(response, Response):
            response.headers[ResponseHeaderKeyEnum.request_id.value] = value
        # for ContextPureMiddleware
        else:
            if response["type"] == "http.response.start":
                headers = MutableHeaders(scope=response)
                headers.append(ResponseHeaderKeyEnum.request_id.value, value)


class RequestStartTimestampPlugin(Plugin):
    """请求开始时间"""

    key = ContextKeyEnum.request_start_timestamp.value

    async def process_request(
        self,
        request: Request | HTTPConnection,
    ) -> float:
        return time.time()


class RequestProcessInfoPlugin(Plugin):
    """请求、响应相关的日志"""

    key = ContextKeyEnum.process_time.value

    async def process_request(
        self,
        request: HTTPConnection,
    ) -> dict:
        return {
            "method": request.scope["method"],
            "uri": request.scope["path"],
            "client": request.scope.get("client", ("", ""))[0],
        }

    async def enrich_response(
        self,
        response: Response | Message,
    ) -> None:
        request_start_timestamp = context.get(RequestStartTimestampPlugin.key)
        if not request_start_timestamp:
            raise RuntimeError("Cannot evaluate process time")
        process_time = (time.time() - float(request_start_timestamp)) * 1000  # ms
        if isinstance(response, Response):
            response.headers[ResponseHeaderKeyEnum.process_time.value] = str(
                process_time,
            )
        else:
            if response["type"] == "http.response.start":
                headers = MutableHeaders(scope=response)
                headers.append(
                    ResponseHeaderKeyEnum.process_time.value,
                    str(process_time),
                )
        info_dict = context.get(self.key)
        info_dict["process_time"] = process_time  # type: ignore
        code = context.get(ContextKeyEnum.response_code.value)
        if code is not None and code != ResponseCodeEnum.success.value:
            data = context.get(ContextKeyEnum.response_data.value)
            info_dict["response_data"] = data  # type: ignore

        logger.info(info_dict)
