from datetime import datetime

from app.definitions.transform import Transform
from app.response import Response


def get_current_time() -> str:
    return datetime.today().strftime('%H-%M-%S_%d-%m-%Y')


class FeedbackTransform(Transform):
    def get_file_name(self, response: Response) -> str:
        postfix = get_current_time()
        tx_id = response.tx_id
        return f'{tx_id}-fb-{postfix}'

    def get_file_content(self, response: Response) -> bytes:
        r: str = response.to_json()
        return bytes(r, 'utf-8')
