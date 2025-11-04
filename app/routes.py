from fastapi import APIRouter, Request, Response, Depends
from sdx_base.models.pubsub import get_message, Message
from starlette.responses import JSONResponse

from app.dependencies import get_survey
from app.survey import Survey

router = APIRouter()


@router.post("/")
async def handle(request: Request, survey: Survey = Depends(get_survey)) -> Response:
    message: Message = await get_message(request)
    survey.process(message)
    return Response(status_code=204)


def unrecoverable_error_handler(_: Request, e: Exception) -> Response:
    # Respond with a 200 to ack the message as no point in retrying
    # Should we be doing more to quarantine?
    return JSONResponse(content={"error": str(e)}, status_code=200)
