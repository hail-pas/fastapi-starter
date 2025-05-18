from fastapi import Request, APIRouter

from util.route import gte_all_uris
from core.response import Resp
from api.second.tags import TagsEnum
from api.second.v1.example import router as example_router

router = APIRouter(prefix="/v1")

router.include_router(example_router, prefix="/example", tags=[TagsEnum.example])


@router.get("/uri-list", tags=[TagsEnum.root], summary="全部uri")
def get_all_urls_from_request(request: Request) -> Resp[list]:
    return Resp(data=gte_all_uris(request.app))  # type: ignore
