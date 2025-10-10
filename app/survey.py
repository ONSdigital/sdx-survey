from typing import Protocol, Optional

from sdx_base.models.pubsub import Message

from app import get_logger
from app.definitions.decrypter import DecryptionBase
from app.definitions.processor import ProcessorBase
from app.definitions.submission import SurveySubmission
from app.definitions.survey_type import V2SurveyType
from app.response import Response
from app.submission_type import get_v2_survey_type

logger = get_logger()


class SurveySettings(Protocol):
    project_id: str
    def get_bucket_name(self) -> str: ...


class BucketReader(Protocol):
    def read(self,
             filename: str,
             bucket_name: str,
             sub_dir: Optional[str] = None,
             project_id: Optional[str] = None) -> bytes:
        ...


class Survey:

    def __init__(self,
                 settings: SurveySettings,
                 bucket_reader: BucketReader,
                 decryption_service: DecryptionBase,
                 survey_processor: ProcessorBase,
                 adhoc_processor: ProcessorBase,
                 feedback_processor: ProcessorBase):

        self._settings = settings
        self._bucket_reader = bucket_reader
        self._decryption_service = decryption_service
        self._survey_processor = survey_processor
        self._adhoc_processor = adhoc_processor
        self._feedback_processor = feedback_processor

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

        bucket_name = self._settings.get_bucket_name()
        data_bytes = self._bucket_reader.read(filename,
                                              bucket_name=bucket_name,
                                              project_id=self._settings.project_id)

        # Sometimes duplicate messages cause the object to not be found.
        # If this is the case then there is nothing to process
        if data_bytes is None:
            return

        encrypted_message_str = data_bytes.decode('utf-8')

        submission: SurveySubmission = self._decryption_service.decrypt_survey(encrypted_message_str)

        response: Response = Response(submission)

        logger.info(f"Survey id: {response.get_survey_id()}")

        processor: ProcessorBase
        v2_survey_type = get_v2_survey_type(response)
        if v2_survey_type == V2SurveyType.FEEDBACK:
            processor = self._feedback_processor

        elif v2_survey_type == V2SurveyType.ADHOC:
            processor = self._adhoc_processor

        else:
            processor = self._survey_processor

        processor.run(response)
