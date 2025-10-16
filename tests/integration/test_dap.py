from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from tests.integration.test_base import TestBase, get_json


class TestDap(TestBase):

    def test_bics(self):
        submission_json = get_json("283.0001.json")
        tx_id = submission_json["tx_id"]
        self.set_survey_submission(tx_id, submission_json)

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_filename = 'c37a3efa-593c-4bab-b49c-bee0613c4fb4.json'

        # actual files
        actual_files = self.get_zip_contents()

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.DAP,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "283",
            "period_id": "201605",
            "ru_ref": "11842491738S"
        }

        # actual context
        actual_context: Context = self.get_context()

        # expected_receipt
        expected_receipt = {
                'caseId': "846b8188-8235-4025-a5ef-5b98c693d6f1",
                'partyId': "UNKNOWN"
            }

        # actual receipt
        actual_receipt = self.get_receipt()

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, actual_context)
        self.assertEqual(expected_receipt, actual_receipt)
        # check comments were stored
        self.mock_datastore.commit_entity.assert_called()
