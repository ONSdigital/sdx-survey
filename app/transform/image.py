import json

from app import sdx_app, CONFIG
from app.definitions import SurveySubmission
from app.transform.formatter import get_image_name


def get_image(submission: SurveySubmission) -> bytes:
    survey_json = json.dumps(submission)
    http_response = sdx_app.http_post(CONFIG.IMAGE_SERVICE_URL, "/image", survey_json)
    return http_response.content


def get_name(submission: SurveySubmission) -> str:
    tx_id = submission["tx_id"]
    return get_image_name(tx_id, 1)
