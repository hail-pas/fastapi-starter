from abc import abstractmethod
from typing import Self, override
from inspect import isclass, isfunction
from contextlib import asynccontextmanager
from collections.abc import Callable, AsyncGenerator

from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from config.main import LocalConfig, local_configs
from core.logger import LogLevelEnum, setup_loguru
from core.response import AesResponse
from config.default import RegisterExtensionConfig
from enhance.monkey_patch import patch


class ApiApplication(FastAPI):
    code: str
    settings: LocalConfig

    @override
    def setup(self) -> None:
        self.code = self.extra["code"]
        self.settings = local_configs
        patch()
        setup_loguru(LogLevelEnum.DEBUG if local_configs.project.debug else LogLevelEnum.INFO)
        super().setup()
        self.enable_sentry()
        # self.enable_static_app()

    def enable_sentry(self) -> None:
        if not self.settings.project.sentry_dsn:
            return

        import sentry_sdk  # type: ignore
        from sentry_sdk.integrations.redis import RedisIntegration  # type: ignore

        sentry_sdk.init(
            dsn=self.settings.project.sentry_dsn,  # type: ignore
            environment=self.settings.project.environment,  # type: ignore
            integrations=[RedisIntegration()],
        )

    def enable_static_app(self) -> None:
        static_files_app = StaticFiles(
            directory=f"{self.settings.server.static_path}/{self.code}",  # type: ignore
        )
        self.mount(
            path=self.settings.server.static_path,  # type: ignore
            app=static_files_app,
            name="static",
        )

    def amount_app_or_router(self, roster: list[tuple[FastAPI | Self | APIRouter, str, str]]) -> None:
        for app_or_router, prefix_path, name in roster:
            assert not prefix_path or prefix_path.startswith(
                "/",
            ), "Routed paths must start with '/'"
            if isinstance(app_or_router, FastAPI):
                self.mount(prefix_path or "", app_or_router, name)
            elif isinstance(app_or_router, APIRouter):
                self.include_router(app_or_router)
            else:
                raise TypeError(f"Invalid type for roster item: {app_or_router}")

    def setup_middleware(self, roster: list) -> None:
        for middle_fc in roster[::-1]:
            if isfunction(middle_fc):
                self.add_middleware(BaseHTTPMiddleware, dispatch=middle_fc)
            else:
                if isclass(middle_fc[0]):  # type: ignore
                    if isinstance(middle_fc[1], dict):  # type: ignore
                        self.add_middleware(middle_fc[0], **middle_fc[1])  # type: ignore
                    else:
                        raise RuntimeError(
                            f"Require Dict as kwargs for middleware class, Got {type(middle_fc[1])}",  # type: ignore
                        )
                else:
                    raise RuntimeError(
                        f"Require Class, Got Type {type(middle_fc[0])}",  # type: ignore
                    )

    def setup_exception_handlers(
        self,
        roster: list[tuple[type[Exception], Callable[..., AesResponse | HTMLResponse | None]]],
    ) -> None:
        for exc, handler in roster:
            self.add_exception_handler(exc, handler)  # type: ignore

    @abstractmethod
    async def before_server_start(self) -> None:
        # 生产环境启动前执行代码, 如数据库迁移等
        raise NotImplementedError


@asynccontextmanager
async def lifespan(api: ApiApplication) -> AsyncGenerator:
    for _, ext_conf in api.settings.extensions:  # type: ignore
        if isinstance(ext_conf, RegisterExtensionConfig):
            await ext_conf.register()

    yield

    for _, ext_conf in api.settings.extensions:  # type: ignore
        if isinstance(ext_conf, RegisterExtensionConfig):
            await ext_conf.unregister()
