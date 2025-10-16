from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from tests.integration.test_base import TestBase, get_json


class TestAdhoc(TestBase):

    def test_phm(self):
        submission_json = get_json("740.0001.json")
        tx_id = submission_json["tx_id"]
        self.set_survey_submission(tx_id, submission_json)

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_filename = 'cebf9e22-0b78-40d8-872d-ca5fe2507ab1.json'

        # actual files
        actual_files = self.get_zip_contents()

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.ADHOC,
            "context_type": ContextType.ADHOC_SURVEY,
            "survey_id": "740",
        }

        # actual context
        actual_context: Context = self.get_context()

        # expected_receipt
        expected_receipt = {
                'data': {
                    'qid': "0130000001408548"
                }
            }

        # actual receipt
        actual_receipt = self.get_receipt()

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, actual_context)
        self.assertEqual(expected_receipt, actual_receipt)
        # check comments were not stored
        self.mock_datastore.commit_entity.assert_not_called()
