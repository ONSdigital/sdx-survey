import logging

from structlog import wrap_logger
from app.comments import store_comments
from app.deliver import deliver_feedback, deliver_survey, deliver_dap
from app.errors import QuarantinableError
from app.receipt import send_receipt
from app.decrypt import decrypt_survey
from app.transform import transform
from app.validate import validate

logger = wrap_logger(logging.getLogger(__name__))

DAP_SURVEYS = ["023", "134", "147", "281", "283", "lms", "census"]


def process(encrypted_message_str: str):

    logger.info("processing message")
    survey_dict = decrypt_survey(encrypted_message_str)

    valid = validate(survey_dict)
    if not valid:
        raise QuarantinableError(f"Invalid survey: {survey_dict['tx_id']}")

    if is_feedback(survey_dict):
        deliver_feedback(survey_dict)

    else:

        store_comments(survey_dict)

        if survey_dict['survey_id'] not in DAP_SURVEYS:
            zip_file = transform(survey_dict)
            deliver_survey(survey_dict, zip_file)
        else:
            deliver_dap(survey_dict)

        send_receipt(survey_dict)


def is_feedback(data: dict) -> bool:
    logger.info(f"Checking for feedback: {data['tx_id']}")
    submission_type = data["type"]
    return "feedback" in submission_type
