import json
from typing import Final

from sdx_gcp import RequestsResponse
from sdx_gcp.app import get_logger

from app import sdx_app
from app import CONFIG

from app.definitions import SurveySubmission
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
            "survey_id": submission["survey_metadata"]["survey_id"],
            "period_id": submission["survey_metadata"]["period_id"],
            "ru_ref": submission["survey_metadata"]["ru_ref"],
            "form_type": submission["survey_metadata"]["form_type"],
            "period_start_date": submission["survey_metadata"]["ref_p_start_date"],
            "period_end_date": submission["survey_metadata"]["ref_p_end_date"],
        }
    )

    return response.content


def get_name(submission: SurveySubmission) -> str:
    survey_id = submission["survey_metadata"]["survey_id"]
    tx_id = submission["tx_id"]
    return f"{survey_id}_{get_tx_code(tx_id)}"
