from typing import Final

import requests

from app import get_logger
from app.definitions.gcp_protocols import Http
from app.definitions.http import ImagePosterBase
from app.response import Response

logger = get_logger()

IMAGE_END_POINT: Final[str] = "image"


class ImagePoster(ImagePosterBase):

    def __init__(self, image_url: str, http_service: Http):
        self._image_url = image_url
        self._http_service = http_service

    def call_image(self, response: Response) -> bytes:
        logger.info("Calling sdx-image...")
        survey_json: str = response.to_json()

        response: requests.Response = self._http_service.post(
            self._image_url,
            IMAGE_END_POINT,
            survey_json,
        )

        return response.content
