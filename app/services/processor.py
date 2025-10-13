from collections.abc import Callable
from typing import Self

from app.definitions.comments import CommentsBase
from app.definitions.context import Context
from app.definitions.deliver import DeliverBase
from app.definitions.processor import ProcessorBase
from app.definitions.receipting import ReceiptServiceBase
from app.definitions.survey_type import SurveyType
from app.definitions.transformer import TransformerBase
from app.response import Response


"""
    This file defines a set of classes
    that are used to process a single
    survey, each processor can run a set
    of actions, actions are simple functions
    that take a Response object and return None
    this could be receipting, storing comments etc
"""

Action = Callable[[Response], None]


class Processor(ProcessorBase):
    """
    The Processor is responsible
    for processing a given survey, extend this
    class to provide logic for processing a specific survey
    """

    def __init__(self: Self):
        self._actions: list[Action] = self.load_actions()

    def load_actions(self) -> list[Action]:
        return []

    def run(self: Self, response: Response):
        """
        The method that processes
        the survey, extract version, run actions
        and deliver
        """
        for action in self._actions:
            action(response)
        self.deliver(response)

    def deliver(self: Self, response: Response):
        pass


class ProcessorV2(Processor):

    def __init__(self,
                 transformer_service: TransformerBase,
                 deliver_service: DeliverBase,
                 receipt_service: ReceiptServiceBase,
                 comments_service: CommentsBase):
        super().__init__()
        self._transformer_service = transformer_service
        self._deliver_service = deliver_service
        self._receipt_service = receipt_service
        self._comments_service = comments_service

    def deliver(self: Self, response: Response):
        zip_file = self._transformer_service.transform(response)
        survey_type = response.get_survey_type()
        context_type = response.get_context_type()
        context: Context = {
            "tx_id": response.tx_id,
            "survey_id": response.get_survey_id(),
            "survey_type": survey_type,
            "context_type": context_type,
        }

        if self._response.get_response_type() != SurveyType.ADHOC:
            context["period_id"] = response.get_period()
            context["ru_ref"] = response.get_ru_ref()

        self._deliver_service.deliver_zip(response.tx_id, zip_file, context)


class SurveyProcessorV2(ProcessorV2):

    def load_actions(self) -> list[Action]:
        return [self._receipt_service.send_receipt, self._comments_service.store_comments]


class AdhocProcessorV2(ProcessorV2):

    def load_actions(self) -> list[Action]:
        return [self._receipt_service.send_receipt]


class FeedbackProcessorV2(ProcessorV2):
    pass
