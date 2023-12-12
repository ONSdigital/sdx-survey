from collections.abc import Callable

from app.comments import store_comments
from app.deliver import deliver_dap, V2, V1, deliver_feedback, ADHOC, deliver_survey, deliver_hybrid
from app.receipt import send_receipt
from app.submission_type import requires_v1_conversion
from app.response import Response, SurveyType
from app.transform.json import convert_v2_to_v1
from app.transform.transform import transform


Action = Callable[[Response],]


class Processor:

    def __init__(self, response: Response):
        self._response = response
        self._actions: list[Action] = []

    def add_actions(self, *actions: Action):
        self._actions.extend(actions)

    def run(self):
        version = self._version()
        for action in self._actions:
            action(self._response)
        self.deliver(version)

    def _version(self) -> str:
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

    def __init__(self, response: Response):
        super().__init__(response)
        self.add_actions(send_receipt)

    def deliver(self, version: str):
        deliver_dap(self._response, version=version)


class SurveyProcessor(Processor):

    def __init__(self, response: Response):
        super().__init__(response)
        self.add_actions(send_receipt, store_comments)

    def deliver(self, version: str):
        zip_file = transform(self._response)
        deliver_survey(self._response, zip_file, version=version)


class HybridProcessor(SurveyProcessor):

    def deliver(self, version: str):
        zip_file = transform(self._response)
        deliver_hybrid(self._response, zip_file, version=version)


class DapProcessor(Processor):

    def __init__(self, response: Response):
        super().__init__(response)
        self.add_actions(send_receipt, store_comments)

    def deliver(self, version: str):
        if requires_v1_conversion(self._response):
            self._response = convert_v2_to_v1(self._response)
        deliver_dap(self._response, version=version)


class PrepopProcessor(SurveyProcessor):

    def __init__(self, response: Response):
        super().__init__(response)
        self.add_actions(send_receipt)

    def deliver(self, version: str):
        pass
