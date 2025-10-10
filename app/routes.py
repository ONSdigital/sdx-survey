from fastapi import APIRouter, Request, Response, Depends
from sdx_base.models.pubsub import get_message, Message

from app.dependencies import get_survey
from app.survey import Survey

router = APIRouter()


@router.post("/")
async def handle(request: Request, survey: Survey = Depends(get_survey)) -> Response:
    message: Message = await get_message(request)
    survey.process(message)
    return Response(status_code=204)
