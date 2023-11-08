from sdx_gcp import Message, TX_ID, Request, get_message
from sdx_gcp.app import get_logger

from app import CONFIG, sdx_app
from app.comments import store_comments
from app.deliver import deliver_feedback, deliver_survey, deliver_dap, deliver_hybrid, ADHOC, V1, V2
from app.receipt import send_receipt
from app.decrypt import decrypt_survey
from app.submission_type import get_response_type, ResponseType, get_survey_type, SurveyType, get_deliver_target, \
    DeliverTarget, get_schema_version, SchemaVersion, get_survey_id, is_new_transform
from app.call_transform import call_legacy_transform
from app.transform.transform import transform
from app.transform.json import requires_converting, convert_v2_to_v1

logger = get_logger()


def get_tx_id_from_object_id(req: Request) -> TX_ID:
    message: Message = get_message(req)
    return message["attributes"]["objectId"]


def process(message: Message, tx_id: TX_ID):

    """
    Orchestrates the required steps to read and process the encrypted json file
    from the filename received in the message.
    The encrypted json can represent either a survey submission or survey feedback.
    The steps include:
        - decryption
        - transformation
        - comment persistence
        - delivery
        - receipting
    and are dependent on the survey and type of the submission.
    """

    logger.info(f"Survey triggered by PubSub with message: {message}")
    attributes = message["attributes"]
    filename = attributes['objectId']

    data_bytes = sdx_app.gcs_read(filename, CONFIG.BUCKET_NAME)
    encrypted_message_str = data_bytes.decode('utf-8')

    submission: dict = decrypt_survey(encrypted_message_str)
    logger.info(f"Survey id: {get_survey_id(submission)}")

    if get_response_type(submission) == ResponseType.FEEDBACK:
        # feedback do not require storing comments, transforming, or receipting.
        if get_schema_version(submission) == SchemaVersion.V2:
            if get_survey_type(submission) == SurveyType.ADHOC:
                v = ADHOC
            else:
                v = V2
        else:
            v = V1

        deliver_feedback(submission, tx_id=tx_id, filename=filename, version=v)

    elif get_survey_type(submission) == SurveyType.ADHOC:
        # adhoc surveys do not require transforming
        send_receipt(submission)
        deliver_dap(submission, tx_id=tx_id, version=ADHOC)

    else:
        send_receipt(submission)
        store_comments(submission)

        version = V2 if get_schema_version(submission) == SchemaVersion.V2 else V1
        deliver_target = get_deliver_target(submission)

        if not is_new_transform(submission):
            if requires_converting(submission):
                version = V1
                submission = convert_v2_to_v1(submission)

        if deliver_target == DeliverTarget.DAP:
            # dap surveys do not require transforming
            deliver_dap(submission, tx_id=tx_id, version=version)

        else:

            if is_new_transform(submission):
                zip_file = transform(submission)
            else:
                zip_file = call_legacy_transform(submission, filename, version)

            if deliver_target == DeliverTarget.HYBRID:
                deliver_hybrid(submission, zip_file, tx_id=tx_id, version=version)
            else:
                deliver_survey(submission, zip_file, tx_id=tx_id, version=version)
