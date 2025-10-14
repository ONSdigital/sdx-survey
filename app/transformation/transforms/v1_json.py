from app.response import Response
from app.transformation.formatter import get_tx_code
from app.definitions.transform import Transform


class V1JsonTransform(Transform):
    def get_file_name(self, response: Response) -> str:
        if response.get_survey_id() == "283":
            return f"{response.tx_id}.json"

        tx_code = get_tx_code(response.tx_id)
        return f"{response.get_survey_id()}_{tx_code}.json"

    def get_file_content(self, response: Response) -> bytes:
        r: str = response.to_v1_json()
        return bytes(r, 'utf-8')
