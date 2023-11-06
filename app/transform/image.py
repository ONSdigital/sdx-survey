import json

from app import sdx_app, CONFIG
from app.definitions import SurveySubmission
from app.transform.formatter import get_tx_code


def get_image(submission: SurveySubmission) -> bytes:
    survey_json = json.dumps(submission)
    http_response = sdx_app.http_post(CONFIG.IMAGE_SERVICE_URL, "/image", survey_json)
    return http_response.content


def get_name(submission: SurveySubmission) -> str:
    tx_id = submission["tx_id"]
    return f"S{get_tx_code(tx_id)}_1.JPG"
