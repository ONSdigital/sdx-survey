import structlog

from app.comments import store_comments
from app.deliver import deliver_feedback, deliver_survey, deliver_dap, deliver_hybrid
from app.errors import QuarantinableError
from app.reader import read
from app.receipt import send_receipt
from app.decrypt import decrypt_survey
from app.transform import transform
from app.validate import validate

logger = structlog.get_logger()

# list of survey ids that target only DAP
DAP_SURVEYS = ["283", "lms", "census"]
# list of surveys that target DAP and Legacy
HYBRID_SURVEYS = ["007", "023", "134", "147"]


def process(tx_id: str):

    """
    Orchestrates the required steps to process an encrypted json string.
    The encrypted json can represent either a survey submission or survey feedback.
    The steps include:
        - decryption
        - validation
        - transformation
        - comment persistence
        - delivery
        - receipting
    and are dependent on the survey and type of the submission.
    """

    logger.info("Processing tx_id")
    data_bytes = read(tx_id)
    encrypted_message_str = data_bytes.decode('utf-8')

    survey_dict = decrypt_survey(encrypted_message_str)

    valid = validate(survey_dict)
    if not valid:
        logger.error("Validation failed, quarantining survey")
        raise QuarantinableError("Invalid survey")

    if is_feedback(survey_dict):
        # feedback do not require storing comments, transforming, or receipting.
        deliver_feedback(survey_dict, filename=tx_id)

    else:
        store_comments(survey_dict)

        survey_id = survey_dict['survey_id']
        if survey_id not in DAP_SURVEYS:
            zip_file = transform(survey_dict)
            if survey_id in HYBRID_SURVEYS:
                deliver_hybrid(survey_dict, zip_file)
            else:
                deliver_survey(survey_dict, zip_file)
        else:
            # dap surveys do not require transforming
            deliver_dap(survey_dict)

        send_receipt(survey_dict)


def is_feedback(data: dict) -> bool:
    logger.info("Checking for feedback")
    submission_type = data["type"]
    return "feedback" in submission_type
