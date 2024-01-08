from sdx_gcp import Message, TX_ID, Request, get_message
from sdx_gcp.app import get_logger

from app import CONFIG, sdx_app
from app.decrypt import decrypt_survey
from app.definitions import SurveySubmission
from app.processor import Processor, FeedbackProcessor, ReceiptOnlyProcessor, AdhocProcessor, DapProcessor, HybridProcessor, \
    SurveyProcessor
from app.response import Response, SurveyType, ResponseType, DeliverTarget
from app.submission_type import receipt_only_submission, get_deliver_target

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

    submission: SurveySubmission = decrypt_survey(encrypted_message_str)

    response: Response = Response(submission, tx_id)

    logger.info(f"Survey id: {response.get_survey_id()}")

    processor: Processor
    if response.get_response_type() == ResponseType.FEEDBACK:
        processor = FeedbackProcessor(response)

    elif receipt_only_submission(response):
        processor = ReceiptOnlyProcessor(response)

    elif response.get_survey_type() == SurveyType.ADHOC:
        processor = AdhocProcessor(response)

    elif get_deliver_target(response) == DeliverTarget.DAP:
        processor = DapProcessor(response)

    elif get_deliver_target(response) == DeliverTarget.HYBRID:
        processor = HybridProcessor(response)

    else:
        processor = SurveyProcessor(response)

    processor.run()
