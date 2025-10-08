from sdx_base.models.pubsub import Message

from app import get_logger
from app.definitions.decrypter import DecryptionBase
from app.definitions.gcp import GcpBase
from app.definitions.submission import SurveySubmission
from app.definitions.survey_type import V2SurveyType
from app.processor import Processor, FeedbackProcessor, ReceiptOnlyProcessor, AdhocProcessor, DapProcessor, \
    HybridProcessor, \
    SurveyProcessor
from app.response import Response, SurveyType, ResponseType, DeliverTarget
from app.submission_type import receipt_only_submission, get_deliver_target, is_v2_nifi_message_submission
from app.v2.processor_v2 import FeedbackProcessorV2, AdhocProcessorV2, SurveyProcessorV2
from app.v2.submission_type_v2 import get_v2_survey_type

logger = get_logger()


class Survey:

    def __init__(self, decryption_service: DecryptionBase, gcp_service: GcpBase):
        self._decryption_service = decryption_service
        self._gcp_service = gcp_service

    def process(self, message: Message):
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

        data_bytes = self._gcp_service.read_bucket(filename)

        # Sometimes duplicate messages cause the object to not be found.
        # If this is the case then there is nothing to process
        if data_bytes is None:
            return

        encrypted_message_str = data_bytes.decode('utf-8')

        submission: SurveySubmission = self._decryption_service.decrypt_survey(encrypted_message_str)

        response: Response = Response(submission)

        logger.info(f"Survey id: {response.get_survey_id()}")

        processor: Processor
        v2_survey_type = get_v2_survey_type(response)
        if v2_survey_type == V2SurveyType.FEEDBACK:
            processor = FeedbackProcessorV2(response)

        elif v2_survey_type == V2SurveyType.ADHOC:
            processor = AdhocProcessorV2(response)

        else:
            processor = SurveyProcessorV2(response)

        processor.run()
