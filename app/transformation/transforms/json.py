from app.response import Response
from app.transformation.formatter import split_ru_ref
from app.definitions.transform import Transform


class JsonTransform(Transform):

    def get_file_name(self, response: Response) -> str:
        ru_ref = split_ru_ref(response.get_ru_ref())[0]
        return f"{response.get_survey_id()}_{ru_ref}_{response.get_period()}.json"

    def get_file_content(self, response: Response) -> bytes:
        r: str = response.to_v1_json()
        return bytes(r, 'utf-8')
