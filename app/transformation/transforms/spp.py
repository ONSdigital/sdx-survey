from datetime import datetime
from typing import Final

from app import get_logger
from app.definitions.http import TransformPosterBase
from app.definitions.transform import Transform
from app.response import Response
from app.transformation.formatter import get_datetime, format_date, split_ru_ref

logger = get_logger()

SPP_DATA_FORMAT: Final[str] = "%Y-%m-%dT%H-%M-%S"

def get_name(response: Response) -> str:
    survey_id = response.get_survey_id()
    ru_ref, _ = split_ru_ref(response.get_ru_ref())
    tx_id = response.get_tx_id()
    timestamp: datetime = get_datetime(response.get_submitted_at())
    postfix: str = format_date(timestamp, SPP_DATA_FORMAT)
    return f"{survey_id}_SDC_{postfix}_{ru_ref}.json"


class SPPTransform(Transform):
    def __init__(self, transformer_post: TransformPosterBase):
        self._transformer_post = transformer_post

    def get_file_name(self, response: Response) -> str:
        return get_name(response)

    def get_file_content(self, response: Response) -> bytes:
        return self._transformer_post.call_transformer_spp(response)
