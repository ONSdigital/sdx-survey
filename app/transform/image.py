from typing import TypedDict, NotRequired

from app import sdx_app, CONFIG
from app.response import Response
from app.transform.formatter import get_tx_code


class ImageResponse(TypedDict):
    questioncode: str
    response: str
    instance: int
    sd_identifier: NotRequired[str]


def get_image(response: Response) -> bytes:
    survey_json: str = response.to_json()
    http_response = sdx_app.http_post(CONFIG.IMAGE_SERVICE_URL, "/image", survey_json)
    return http_response.content


def get_name(response: Response) -> str:
    tx_id = response.get_tx_id()
    return f"S{get_tx_code(tx_id)}_1.JPG"
