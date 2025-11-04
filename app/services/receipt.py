import json
from typing import Protocol

from sdx_base.errors.errors import DataError

from app import get_logger
from app.definitions.receipting import ReceiptServiceBase
from app.response import Response, SurveyType

logger = get_logger()


class ReceiptSettings(Protocol):
    receipt_topic_path: str
    srm_receipt_topic_path: str


class ReceiptPublisher(Protocol):
    def publish_message(self, topic_path: str, message: str, attributes: dict[str, str]) -> str: ...


class ReceiptService(ReceiptServiceBase):
    def __init__(self, settings: ReceiptSettings, receipt_publisher: ReceiptPublisher):
        self._settings = settings
        self._receipt_publisher = receipt_publisher

    def send_receipt(self, response: Response):
        """Creates and publishes a receipt to the receipt topic"""

        logger.info("Receipting...")
        tx_id = response.get_tx_id()

        receipt_str: str
        topic_path: str
        if response.get_survey_type() == SurveyType.ADHOC:
            receipt_str = self._make_srm_receipt(response)
            topic_path = self._settings.srm_receipt_topic_path
        else:
            receipt_str = self._make_receipt(response)
            topic_path = self._settings.receipt_topic_path

        self._receipt_publisher.publish_message(topic_path, receipt_str, attributes={"tx_id": tx_id})
        logger.info("Successfully Receipted")

    def _make_receipt(self, response: Response) -> str:
        """Creates a receipt for RASRM"""
        try:
            receipt_json = {"caseId": response.get_case_id(), "partyId": response.get_user_id()}
        except KeyError as e:
            raise DataError(f"Failed to make receipt: {str(e)}")

        logger.info("Generated receipt", extra={"caseId": receipt_json["caseId"], "partyId": receipt_json["partyId"]})
        receipt_str = json.dumps(receipt_json)
        return receipt_str

    def _make_srm_receipt(self, response: Response) -> str:
        """Creates a receipt for SRM"""
        try:
            receipt_json = {"data": {"qid": response.get_qid()}}
        except KeyError as e:
            raise DataError(f"Failed to make receipt: {str(e)}")

        logger.info("Generated SRM receipt", extra={"qid": receipt_json["data"]})
        receipt_str = json.dumps(receipt_json)
        return receipt_str
