from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from tests.integration.test_base import TestBase, get_json


class TestFeedback(TestBase):

    def test_feedback(self):
        submission_json = get_json("139.fb.json")
        tx_id = submission_json["tx_id"]
        self.set_survey_submission(tx_id, submission_json)

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_filename = 'cc7635a7-f204-4702-88a8-f1814e8d7295-fb-15-02-07_20-04-2021'

        # actual files
        actual_files = self.get_zip_contents()

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.FEEDBACK,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "139",
            'period_id': '1706',
            'ru_ref': '11110000002H',
        }

        # actual context
        actual_context: Context = self.get_context()

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, actual_context)
        self.assertFalse(self.receipt_called)
        # check comments were not stored
        self.mock_datastore.commit_entity.assert_not_called()

    def test_adhoc_feedback(self):
        submission_json = get_json("740.fb.json")
        tx_id = submission_json["tx_id"]
        self.set_survey_submission(tx_id, submission_json)

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_filename = 'ea82c224-0f80-41cc-b877-8a7804b56c26-fb-16-37-56_21-05-2016'

        # actual files
        actual_files = self.get_zip_contents()

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.FEEDBACK,
            "context_type": ContextType.ADHOC_SURVEY,
            "survey_id": "740",
        }

        # actual context
        actual_context: Context = self.get_context()

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, actual_context)
        self.assertFalse(self.receipt_called)
        # check comments were not stored
        self.mock_datastore.commit_entity.assert_not_called()