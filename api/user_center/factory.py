from typing import Literal

from aerich import Command

from core.api import ApiApplication, lifespan
from config.main import local_configs
from core.response import Resp
from core.middleware import roster as middleware_roster
from core.exc_handler import roster as exception_handler_roster
from api.user_center.v1 import router as v1_router
from api.user_center.v2 import router as v2_router
from ext.ext_tortoise.main import ConnectionNameEnum
from ext.ext_tortoise.migrate.env import VERSION_FILE_PATH


class UserCenterApi(ApiApplication):
    async def before_server_start(self) -> None:
        command = Command(
            tortoise_config=self.settings.extensions.relation.to_dict(),
            app=ConnectionNameEnum.user_center.value,
            location=VERSION_FILE_PATH,
        )
        await command.init()
        await command.upgrade(run_in_transaction=True)


user_center_api = UserCenterApi(
    code="UserCenter",
    settings=local_configs,
    title="用户中心",
    description="统一用户管理中心",
    lifespan=lifespan,
    version="1.0.0",
    redirection_url="/docs",
    swagger_ui_parameters={
        "url": "openapi.json",
        "persistAuthorization": local_configs.project.debug,
    },
    servers=[
        {
            "url": str(server.url) + "user",
            "description": server.description,
        }
        for server in local_configs.project.swagger_servers
    ],
)

user_center_api.setup_middleware(roster=middleware_roster)
user_center_api.setup_exception_handlers(roster=exception_handler_roster)

user_center_api.amount_app_or_router(roster=[(v1_router, "", "v1")])
user_center_api.amount_app_or_router(roster=[(v2_router, "", "v2")])


@user_center_api.get("/health", summary="健康检查")
async def health() -> Resp[dict[Literal["status"], Literal["ok"]]]:
    """
    健康检查
    """
    return Resp(data={"status": "ok"})
