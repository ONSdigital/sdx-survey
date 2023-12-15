from app.response import Response
from app.submission_type import requires_v1_conversion
from app.transform.formatter import get_tx_code


def get_contents(response: Response) -> bytes:

    if requires_v1_conversion(response):
        r: str = response.to_v1_json()
    else:
        r: str = response.to_json()

    return bytes(r, 'utf-8')


def get_name(response: Response):
    return "{0}_{1}.json".format(response.get_survey_id(), get_tx_code(response.get_tx_id()))
