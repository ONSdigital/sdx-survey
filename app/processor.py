from collections.abc import Callable

from app.call_transform import call_legacy_transform
from app.comments import store_comments
from app.deliver import deliver_dap, V2, V1, deliver_feedback, ADHOC, deliver_survey, deliver_hybrid
from app.receipt import send_receipt
from app.submission_type import requires_v1_conversion
from app.response import Response, SurveyType
from app.transform.json import convert_v2_to_v1
from app.transform.transform import transform

"""
    This file defines a set of classes
    that are used to process a single
    survey, each processor can run a set
    of actions, actions are simple functions
    that take a Response object and return None
    this could be receipting, storing comments etc
"""

Action = Callable[[Response], None]


class Processor:
    """
    The Processor is responsible
    for processing a given survey, extend this
    class to provide logic for processing a specific survey
    """

    def __init__(self, response: Response):
        self._response = response
        self._actions: list[Action] = self.load_actions()

    def load_actions(self) -> list[Action]:
        return []

    def run(self):
        """
        The method that processes
        the survey, extract version, run actions
        and deliver
        """
        version = self._version()
        for action in self._actions:
            action(self._response)
        self.deliver(version)

    def _version(self) -> str:
        """
        Extract the appropriate version from
        the survey response
        """
        if self._response.get_survey_type() == SurveyType.ADHOC:
            return ADHOC
        else:
            if requires_v1_conversion(self._response):
                return V1
            return V2

    def deliver(self, version: str):

        pass


class FeedbackProcessor(Processor):

    def deliver(self, version: str):
        deliver_feedback(self._response, version=version)


class AdhocProcessor(Processor):

    def load_actions(self) -> list[Action]:
        return [send_receipt]

    def deliver(self, version: str):
        deliver_dap(self._response, version=version)


class SurveyProcessor(Processor):

    def load_actions(self) -> list[Action]:
        return [send_receipt, store_comments]

    def deliver(self, version: str):
        zip_file = transform(self._response)
        deliver_survey(self._response, zip_file, version=version)


class HybridProcessor(SurveyProcessor):

    def deliver(self, version: str):
        zip_file = transform(self._response)
        deliver_hybrid(self._response, zip_file, version=version)


class LegacyHybridProcessor(HybridProcessor):

    def deliver(self, version: str):
        zip_file = call_legacy_transform(self._response, version=version)
        deliver_hybrid(self._response, zip_file, version=version)


class DapProcessor(Processor):

    def load_actions(self) -> list[Action]:
        return [send_receipt, store_comments]

    def deliver(self, version: str):
        if requires_v1_conversion(self._response):
            self._response = convert_v2_to_v1(self._response)
        deliver_dap(self._response, version=version)


class PrepopProcessor(SurveyProcessor):

    def load_actions(self) -> list[Action]:
        return [send_receipt]

    def deliver(self, version: str):
        pass
