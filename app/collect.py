from sdx_gcp import Message, TX_ID, Request, get_message
from sdx_gcp.app import get_logger

from app import CONFIG, sdx_app
from app.decrypt import decrypt_survey
from app.definitions.submission import SurveySubmission
from app.definitions.v2_survey_type import V2SurveyType
from app.processor import Processor, FeedbackProcessor, ReceiptOnlyProcessor, AdhocProcessor, DapProcessor, \
    HybridProcessor, \
    SurveyProcessor
from app.response import Response, SurveyType, ResponseType, DeliverTarget
from app.submission_type import receipt_only_submission, get_deliver_target, v2_nifi_message_submission
from app.v2.processor_v2 import FeedbackProcessorV2, AdhocProcessorV2, SurveyProcessorV2
from app.v2.submission_type_v2 import get_v2_survey_type

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

    # Sometimes duplicate messages cause the object to not be found.
    # If this is the case then there is nothing to process
    if data_bytes is None:
        return

    encrypted_message_str = data_bytes.decode('utf-8')

    submission: SurveySubmission = decrypt_survey(encrypted_message_str)

    response: Response = Response(submission, tx_id)

    logger.info(f"Survey id: {response.get_survey_id()}")

    processor: Processor
    if v2_nifi_message_submission(response):
        v2_survey_type = get_v2_survey_type(response)
        if v2_survey_type == V2SurveyType.FEEDBACK:
            processor = FeedbackProcessorV2(response)

        elif v2_survey_type == V2SurveyType.ADHOC:
            processor = AdhocProcessorV2(response)

        else:
            processor = SurveyProcessorV2(response)

    else:
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
