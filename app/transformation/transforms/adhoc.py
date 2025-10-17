import json

from app.response import Response
from app.definitions.transform import Transform


class AdhocTransform(Transform):
    def get_file_name(self, response: Response) -> str:
        return f"{response.get_tx_id()}.json"

    def get_file_content(self, response: Response) -> bytes:
        r: str = json.dumps(response.get_submission())
        return bytes(r, "utf-8")
