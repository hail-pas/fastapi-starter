from typing import Literal

from aerich import Command

from core.api import ApiApplication, lifespan
from config.main import local_configs
from api.second.v1 import router as v1_router
from api.second.v2 import router as v2_router
from core.response import Resp
from core.middleware import roster as middleware_roster
from core.exc_handler import roster as exception_handler_roster
from ext.ext_tortoise.main import ConnectionNameEnum
from ext.ext_tortoise.migrate.env import VERSION_FILE_PATH


class ExampleApi(ApiApplication):
    async def before_server_start(self) -> None:
        command = Command(
            tortoise_config=self.settings.extensions.relation.to_dict(),
            app=ConnectionNameEnum.second.value,
            location=VERSION_FILE_PATH,
        )
        await command.init()
        await command.upgrade(run_in_transaction=True)


second_api = ExampleApi(
    code="Example",
    settings=local_configs,
    title="Example",
    description="Example",
    lifespan=lifespan,
    version="1.0.0",
    redirection_url="/docs",
    swagger_ui_parameters={
        "url": "openapi.json",
        "persistAuthorization": local_configs.project.debug,
    },
    servers=[
        {
            "url": str(server.url) + "example",
            "description": server.description,
        }
        for server in local_configs.project.swagger_servers
    ],
)

second_api.setup_middleware(roster=middleware_roster)
second_api.setup_exception_handlers(roster=exception_handler_roster)

second_api.amount_app_or_router(roster=[(v1_router, "", "v1")])
second_api.amount_app_or_router(roster=[(v2_router, "", "v2")])


@second_api.get("/health", summary="健康检查")
async def health() -> Resp[dict[Literal["status"], Literal["ok"]]]:
    """
    健康检查
    """
    return Resp(data={"status": "ok"})
