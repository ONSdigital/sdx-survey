import json
from typing import Final

from sdx_gcp import RequestsResponse
from sdx_gcp.app import get_logger

from app import sdx_app
from app import CONFIG

from app.definitions import SurveySubmission
from app.submission_type import get_survey_id, get_period, get_field, get_ru_ref, get_form_type, get_period_start_date, \
    get_period_end_date
from app.transform.formatter import get_tx_code

logger = get_logger()

END_POINT: Final = "pck"


def get_contents(submission: SurveySubmission) -> bytes:
    logger.info("Calling sdx-transformer...")
    survey_data = json.dumps(submission["data"])
    endpoint = END_POINT
    tx_id = submission["tx_id"]
    response: RequestsResponse = sdx_app.http_post(
        CONFIG.TRANSFORMER_SERVICE_URL,
        endpoint,
        survey_data,
        params={
            "tx_id": tx_id,
            "survey_id": get_survey_id(submission),
            "period_id": get_period(submission),
            "ru_ref": get_ru_ref(submission),
            "form_type": get_form_type(submission),
            "period_start_date": get_period_start_date(submission),
            "period_end_date": get_period_end_date(submission),
        }
    )

    return response.content


def get_name(submission: SurveySubmission) -> str:
    survey_id = submission["survey_metadata"]["survey_id"]
    if survey_id == "202":
        survey_id = get_abs_survey_id(submission["survey_metadata"]["form_type"])

    if survey_id in ["182", "183", "184", "185"]:
        survey_id = "181"

    tx_id = submission["tx_id"]
    return f"{survey_id}_{get_tx_code(tx_id)}"


# a dictionary mapping the form type to the sector id required downstream
form_map = {'1802': '053',
            '1804': '051',
            '1808': '050',
            '1810': '055',
            '1812': '052',
            '1814': '052',
            '1818': '052',
            '1820': '052',
            '1824': '052',
            '1826': '052',
            '1862': '001',
            '1864': '001',
            '1874': '001',
            '1805': '054',
            '1875': '001',
            '1865': '001',
            '1863': '001',
            '1819': '052',
            '1825': '052',
            '1806': '054',
            '1815': '052',
            '1827': '052',
            '1821': '052',
            '1867': '001',
            '1869': '001',
            '1871': '001',
            '1877': '001',
            '1879': '001',
            '1801': '053',
            '1803': '051',
            '1807': '050',
            '1809': '055',
            '1811': '052',
            '1813': '052',
            '1817': '052',
            '1823': '052',
            '1861': '001',
            '1873': '001',
            }


def get_abs_survey_id(formtype: str) -> str:
    return form_map.get(formtype)
