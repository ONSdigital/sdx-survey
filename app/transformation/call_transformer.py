import json
from typing import Final

from sdx_gcp import RequestsResponse
from sdx_gcp.app import get_logger

from app import CONFIG
from app import sdx_app
from app.response import Response

logger = get_logger()

PCK_END_POINT: Final[str] = "pck"
SPP_END_POINT: Final[str] = "spp"


def call_transformer_pck(response: Response) -> bytes:
    return _call_transformer(response, PCK_END_POINT)


def call_transformer_spp(response: Response) -> bytes:
    return _call_transformer(response, SPP_END_POINT)


def _call_transformer(response: Response, endpoint: str) -> bytes:
    logger.info("Calling sdx-transformer...")
    survey_data = json.dumps(response.get_data())

    tx_id = response.get_tx_id()
    response: RequestsResponse = sdx_app.http_post(
        CONFIG.TRANSFORMER_SERVICE_URL,
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
            "use_image_formatter": False,
            "data_version": response.get_data_version()
        }
    )

    return response.content
