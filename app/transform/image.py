import json
from typing import TypedDict, NotRequired

from app import sdx_app, CONFIG
from app.response import Response
from app.transform.call_transformer import call_transformer
from app.transform.formatter import get_tx_code


class ImageResponse(TypedDict):
    questioncode: str
    response: str
    instance: int
    sd_identifier: NotRequired[str]


def get_image(response: Response) -> bytes:
    if response.get_data_version() == "0.0.3":
        image_data_bytes: bytes = call_transformer(response, use_image_formatter=True)
        image_data: list[ImageResponse] = json.loads(image_data_bytes)
        submission: dict[str, any] = response.get_submission()

        submission["data"] = image_data
        data = response.get_data()
        if "supplementary_data" in data:
            submission["supplementary_data"] = data["supplementary_data"]

        survey_json: str = json.dumps(submission)
    else:
        survey_json: str = response.to_json()

    http_response = sdx_app.http_post(CONFIG.IMAGE_SERVICE_URL, "/image", survey_json)
    return http_response.content


def get_name(response: Response) -> str:
    tx_id = response.get_tx_id()
    return f"S{get_tx_code(tx_id)}_1.JPG"
