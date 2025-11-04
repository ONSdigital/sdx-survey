from app.definitions.http import ImagePosterBase
from app.response import Response
from app.transformation.formatter import get_tx_code
from app.definitions.transform import Transform


def get_name(response: Response) -> str:
    tx_id = response.get_tx_id()
    return f"S{get_tx_code(tx_id)}_1.JPG"


class ImageTransform(Transform):
    def __init__(self, image_poster: ImagePosterBase):
        self._image_poster = image_poster

    def get_file_name(self, response: Response) -> str:
        return get_name(response)

    def get_file_content(self, response: Response) -> bytes:
        return self._image_poster.call_image(response)
