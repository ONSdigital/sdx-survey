from app.comments import store_comments
from app.deliver import deliver_dap, V2, V1, deliver_feedback, ADHOC, deliver_survey, deliver_hybrid
from app.receipt import send_receipt
from app.submission_type import requires_v1_conversion
from app.response import Response, SurveyType
from app.transform.json import convert_v2_to_v1
from app.transform.transform import transform


class Processor:

    def __init__(self, response: Response):
        self._response = response
        self._tx_id = response.get_tx_id()

    def run(self):
        version: str = self.version()
        self.receipt()
        self.comments()
        zip_file: bytes = self.transform()
        self.deliver(zip_file, version)

    def version(self) -> str:
        if self._response.get_survey_type() == SurveyType.ADHOC:
            return ADHOC
        else:
            if requires_v1_conversion(self._response):
                return V1
            return V2

    def receipt(self):
        pass

    def comments(self):
        pass

    def transform(self) -> bytes | None:
        pass

    def deliver(self, zip_file: bytes | None, version: str):
        pass


class FeedbackProcessor(Processor):

    def __init__(self, response: Response, filename: str):
        super().__init__(response)
        self.filename = filename

    def deliver(self, _zip_file: None, version: str):
        deliver_feedback(
            self._response,
            tx_id=self._tx_id,
            filename=self.filename,
            version=version)


class SurveyProcessor(Processor):

    def receipt(self):
        send_receipt(self._response)

    def comments(self):
        store_comments(self._response)

    def transform(self) -> bytes:
        return transform(self._response)

    def deliver(self, zip_file: bytes, version: str):
        deliver_survey(self._response, zip_file, tx_id=self._tx_id, version=version)


class HybridProcessor(SurveyProcessor):

    def deliver(self, zip_file: bytes, version: str):
        deliver_hybrid(self._response, zip_file, tx_id=self._tx_id, version=version)


class DapProcessor(SurveyProcessor):

    def transform(self) -> None:
        if requires_v1_conversion(self._response):
            self._response = convert_v2_to_v1(self._response)

    def deliver(self, _zip_file: None, version: str):
        deliver_dap(self._response, tx_id=self._tx_id, version=version)


class AdhocProcessor(DapProcessor):

    def comments(self):
        pass


class PrepopProcessor(SurveyProcessor):

    def comments(self):
        pass

    def transform(self) -> bytes | None:
        pass

    def deliver(self, zip_file: bytes | None, version: str):
        pass
