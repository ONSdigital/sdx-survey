from app import sdx_app, CONFIG
from app.response import Response
from app.transform.formatter import get_tx_code
from app.definitions.transform import Transform


def get_image(response: Response) -> bytes:
    survey_json: str = response.to_json()
    http_response = sdx_app.http_post(CONFIG.IMAGE_SERVICE_URL, "image", survey_json)
    return http_response.content


def get_name(response: Response) -> str:
    tx_id = response.get_tx_id()
    return f"S{get_tx_code(tx_id)}_1.JPG"


class ImageTransform(Transform):

    def get_file_name(self, response: Response) -> str:
        return get_name(response)

    def get_file_content(self, response: Response) -> bytes:
        return get_image(response)
