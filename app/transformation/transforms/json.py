from app.response import Response
from app.submission_type import requires_v1_conversion, requires_json_name_change, requires_json_transform
from app.transformation.call_transformer import call_transformer_spp
from app.transformation.formatter import get_tx_code, split_ru_ref
from app.definitions.transform import Transform


def get_contents(response: Response) -> bytes:

    if requires_json_transform(response):
        return call_transformer_spp(response)

    if requires_v1_conversion(response):
        r: str = response.to_v1_json()
    else:
        r: str = response.to_json()

    return bytes(r, 'utf-8')


def get_name(response: Response):
    if requires_json_name_change(response):
        ru_ref = split_ru_ref(response.get_ru_ref())[0]
        return f"{response.get_survey_id()}_{ru_ref}_{response.get_period()}.json"

    return "{0}_{1}.json".format(response.get_survey_id(), get_tx_code(response.get_tx_id()))


class JsonTransform(Transform):

    def get_file_name(self, response: Response) -> str:
        return get_name(response)

    def get_file_content(self, response: Response) -> bytes:
        return get_contents(response)
