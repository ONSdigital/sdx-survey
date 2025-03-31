from datetime import datetime
from typing import Final

from sdx_gcp.app import get_logger

from app.response import Response
from app.transformation.call_transformer import call_transformer_spp
from app.definitions.transform import Transform
from app.transformation.formatter import get_datetime, format_date

logger = get_logger()

SPP_DATA_FORMAT: Final[str] = "%Y-%m-%dT%H-%M-%S"


def get_contents(response: Response) -> bytes:
    return call_transformer_spp(response)


def get_name(response: Response) -> str:
    survey_id = response.get_survey_id()
    tx_id = response.get_tx_id()
    timestamp: datetime = get_datetime(response.get_submitted_at())
    postfix: str = format_date(timestamp, SPP_DATA_FORMAT)
    return f"{survey_id}_SDC_{postfix}_{tx_id}.json"


class SPPTransform(Transform):

    def get_file_name(self, response: Response) -> str:
        return get_name(response)

    def get_file_content(self, response: Response) -> bytes:
        return get_contents(response)
