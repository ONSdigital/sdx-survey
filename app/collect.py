import logging

from structlog import wrap_logger

from app.comments import store_comments
from app.deliver import deliver_feedback, deliver_survey, deliver_dap
from app.errors import QuarantinableError
from app.receipt import send_receipt
from app.encryption import decrypt_survey
from app.quarantine import quarantine_submission
from app.transform import transform
from app.validate import validate

logger = wrap_logger(logging.getLogger(__name__))

DAP_SURVEYS = ["023", "134", "147", "281", "283", "lms", "census"]


def process(encrypted_message_str: str):

    logger.info("processing message")
    survey_dict = decrypt_survey(encrypted_message_str)
    tx_id = extract_tx_id(survey_dict)

    try:

        validate(survey_dict)

        if is_feedback(survey_dict):
            deliver_feedback(survey_dict)

        else:

            if survey_dict['survey_id'] not in DAP_SURVEYS:
                zip_file = transform(survey_dict)
                deliver_survey(survey_dict, zip_file)
            else:
                deliver_dap(survey_dict)

            store_comments(survey_dict)

            send_receipt(survey_dict)

    except QuarantinableError as e:
        logger.info("quarantining message")
        logger.error(str(e))
        quarantine_submission(encrypted_message_str, tx_id)


def extract_tx_id(message_dict: dict) -> str:
    return message_dict['tx_id']


def is_feedback(data: dict) -> bool:
    submission_type = data["type"]
    return "feedback" in submission_type
