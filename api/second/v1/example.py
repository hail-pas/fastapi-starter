from fastapi import Request, APIRouter

from core.response import Resp

router = APIRouter()


@router.post("", summary="example", description="example")
async def example(request: Request) -> Resp:
    return Resp(data="ok")
