from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from config.main import local_configs
from config.default import RegisterExtensionConfig


async def init_ctx():
    for _, ext_conf in local_configs.extensions:  # type: ignore
        if isinstance(ext_conf, RegisterExtensionConfig):
            await ext_conf.register()


async def clear_ctx():
    for _, ext_conf in local_configs.extensions:  # type: ignore
        if isinstance(ext_conf, RegisterExtensionConfig):
            await ext_conf.unregister()


@asynccontextmanager
async def ctx() -> AsyncGenerator:
    await init_ctx()

    yield

    await clear_ctx()
