import structlog

from app.comments import store_comments
from app.deliver import deliver_feedback, deliver_survey, deliver_dap, deliver_hybrid, ADHOC, V1, V2
from app.errors import QuarantinableError
from app.reader import read
from app.receipt import send_receipt
from app.decrypt import decrypt_survey
from app.submission_type import get_response_type, ResponseType, get_survey_type, SurveyType, get_deliver_target, \
    DeliverTarget, get_schema_version, SchemaVersion
from app.transform import transform
from app.validate import validate

logger = structlog.get_logger()


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

    submission: dict = decrypt_survey(encrypted_message_str)

    valid = validate(submission)
    if not valid:
        logger.error("Validation failed, quarantining survey")
        raise QuarantinableError("Invalid survey")

    if get_response_type(submission) == ResponseType.FEEDBACK:
        # feedback do not require storing comments, transforming, or receipting.
        deliver_feedback(submission, filename=tx_id)

    elif get_survey_type(submission) == SurveyType.ADHOC:
        deliver_dap(submission, ADHOC)
        send_receipt(submission)

    else:
        store_comments(submission)

        version = V2 if get_schema_version(submission) == SchemaVersion.V2 else V1
        deliver_target = get_deliver_target(submission)

        if deliver_target == DeliverTarget.DAP:
            # dap surveys do not require transforming
            deliver_dap(submission, version)

        else:
            zip_file = transform(submission)
            if deliver_target == DeliverTarget.HYBRID:
                deliver_hybrid(submission, zip_file, version)
            else:
                deliver_survey(submission, zip_file, version)

        send_receipt(submission)
