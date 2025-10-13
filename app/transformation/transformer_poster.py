import json
from typing import Final

import requests

from app import get_logger
from app.definitions.gcp_protocols import Http
from app.definitions.http import TransformPosterBase
from app.response import Response

logger = get_logger()

PCK_END_POINT: Final[str] = "PCK"
SPP_END_POINT: Final[str] = "spp"


class TransformPoster(TransformPosterBase):

    def __init__(self, transformer_url: str, http_service: Http):
        self._transformer_url = transformer_url
        self._http_service = http_service

    def call_transformer_pck(self, response: Response) -> bytes:
        return self._call_transformer(response, PCK_END_POINT)

    def call_transformer_spp(self, response: Response) -> bytes:
        return self._call_transformer(response, SPP_END_POINT)

    def _call_transformer(self, response: Response, endpoint: str) -> bytes:
        logger.info("Calling sdx-transformer...")
        survey_data = json.dumps(response.get_data())

        tx_id = response.get_tx_id()
        response: requests.Response = self._http_service.post(
            self._transformer_url,
            endpoint,
            survey_data,
            params={
                "tx_id": tx_id,
                "survey_id": response.get_survey_id(),
                "period_id": response.get_period(),
                "ru_ref": response.get_ru_ref(),
                "form_type": response.get_form_type(),
                "period_start_date": response.get_period_start_date(),
                "period_end_date": response.get_period_end_date(),
                "data_version": response.get_data_version()
            }
        )

        return response.content
