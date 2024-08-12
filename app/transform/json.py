from app.response import Response
from app.submission_type import requires_v1_conversion, requires_json_name_change, requires_json_transform
from app.transform.call_transformer import call_transformer
from app.transform.formatter import get_tx_code, split_ru_ref


def get_contents(response: Response) -> bytes:

    if requires_json_transform(response):
        return call_transformer(response)

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
