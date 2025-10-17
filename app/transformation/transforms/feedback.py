from datetime import datetime
from typing import Final

from app.definitions.transform import Transform
from app.response import Response
from app.transformation.formatter import get_datetime, format_date


FEEDBACK_DATA_FORMAT: Final[str] = '%H-%M-%S_%d-%m-%Y'


class FeedbackTransform(Transform):
    def get_file_name(self, response: Response) -> str:
        timestamp: datetime = get_datetime(response.get_submitted_at())
        postfix: str = format_date(timestamp, FEEDBACK_DATA_FORMAT)
        tx_id = response.get_tx_id()
        return f'{tx_id}-fb-{postfix}'

    def get_file_content(self, response: Response) -> bytes:
        r: str = response.to_json()
        return bytes(r, 'utf-8')
