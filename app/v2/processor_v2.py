from typing import Self

from app.comments import store_comments
from app.definitions.v2_survey_type import V2SurveyType
from app.processor import Processor, Action
from app.services.receipt import send_receipt
from app.transformation.create import transform
from app.v2.context import Context
from app.v2.deliver_v2 import deliver_zip
from app.v2.submission_type_v2 import get_v2_survey_type, get_v2_context_type


class ProcessorV2(Processor):

    def deliver(self: Self, _version):
        zip_file = transform(self._response)
        survey_type = get_v2_survey_type(self._response)
        context_type = get_v2_context_type(survey_type)
        context: Context = {
            "tx_id": self._response.tx_id,
            "survey_id": self._response.get_survey_id(),
            "survey_type": survey_type,
            "context_type": context_type,
        }

        if self._response.get_response_type() != V2SurveyType.ADHOC:
            context["period_id"] = self._response.get_period()
            context["ru_ref"] = self._response.get_ru_ref()

        deliver_zip(self._response.tx_id, zip_file, context)


class SurveyProcessorV2(ProcessorV2):

    def load_actions(self) -> list[Action]:
        return [send_receipt, store_comments]


class AdhocProcessorV2(ProcessorV2):

    def load_actions(self) -> list[Action]:
        return [send_receipt]


class FeedbackProcessorV2(ProcessorV2):
    pass
