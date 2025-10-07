import json
from typing import Protocol

from sdx_base.errors.errors import DataError

from app import get_logger
from app.definitions.gcp import GcpBase
from app.response import Response, SurveyType

logger = get_logger()


class ReceiptSettings(Protocol):
    receipt_topic_path: str
    srm_receipt_topic_path: str


class ReceiptService:

    def __init__(self, settings: ReceiptSettings, gcp: GcpBase):
        self._settings = settings
        self._gcp = gcp

    def send_receipt(self, response: Response):
        """Creates and publishes a receipt to the receipt topic"""

        logger.info("Receipting...")
        tx_id = response.get_tx_id()

        receipt_str: str
        topic_path: str
        if response.get_survey_type() == SurveyType.ADHOC:
            receipt_str = self.make_srm_receipt(response)
            topic_path = self._settings.srm_receipt_topic_path
        else:
            receipt_str = self.make_receipt(response)
            topic_path = self._settings.receipt_topic_path

        self._gcp.publish_message(receipt_str, tx_id, topic_path)
        logger.info('Successfully Receipted')

    def make_receipt(self, response: Response) -> str:
        """Creates a receipt for RASRM"""
        try:
            receipt_json = {
                'caseId': response.get_case_id(),
                'partyId': response.get_user_id()
            }
        except KeyError as e:
            raise DataError(f'Failed to make receipt: {str(e)}')

        logger.info('Generated receipt', extra={"caseId": receipt_json['caseId'], "partyId":receipt_json['partyId']})
        receipt_str = json.dumps(receipt_json)
        return receipt_str


    def make_srm_receipt(self, response: Response) -> str:
        """Creates a receipt for SRM"""
        try:
            receipt_json = {
                'data': {
                    'qid': response.get_qid()
                }
            }
        except KeyError as e:
            raise DataError(f'Failed to make receipt: {str(e)}')

        logger.info('Generated SRM receipt', extra={"qid": receipt_json['data']})
        receipt_str = json.dumps(receipt_json)
        return receipt_str
