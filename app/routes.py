from fastapi import APIRouter, Request, Response
from sdx_base.models.pubsub import get_message, Message

from app.collect import process

router = APIRouter()


@router.post("/")
async def handle(request: Request) -> Response:
    message: Message = await get_message(request)
    process(message)
    return Response(status_code=204)
