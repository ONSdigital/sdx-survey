from typing import Self

from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from tests.integration.test_base import TestBase


class TestFeedback(TestBase):
    def test_feedback(self: Self):
        object_id = "11111111-2222-3333-4444-55555555"
        self.set_feedback_submission("139.fb.json", object_id)

        resp = self.client.post("/", json=self.envelope)

        expected_filename = "cc7635a7-f204-4702-88a8-f1814e8d7295-fb-15-02-07_20-04-2021"

        actual_files = self.get_zip_contents()

        expected_context: Context = {
            "tx_id": "cc7635a7-f204-4702-88a8-f1814e8d7295",
            "survey_type": SurveyType.FEEDBACK,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "139",
            "period_id": "1706",
            "ru_ref": "11110000002H",
        }

        self.assertTrue(resp.is_success)
        self.assertEqual(object_id, self.get_zip_name())
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, self.get_context())
        self.assertFalse(self.receipt_called)
        # check comments were not stored
        self.mock_datastore.commit_entity.assert_not_called()

    def test_adhoc_feedback(self: Self):
        object_id = "11111111-2222-3333-4444-55555555"
        self.set_feedback_submission("740.fb.json", object_id)

        resp = self.client.post("/", json=self.envelope)

        expected_filename = "ea82c224-0f80-41cc-b877-8a7804b56c26-fb-16-37-56_21-05-2016"

        actual_files = self.get_zip_contents()

        expected_context: Context = {
            "tx_id": "ea82c224-0f80-41cc-b877-8a7804b56c26",
            "survey_type": SurveyType.FEEDBACK,
            "context_type": ContextType.ADHOC_SURVEY,
            "survey_id": "740",
            "title": "covid_resp_inf_surv_response",
            "label": "phm_740_health_insights_2024",
        }

        self.assertTrue(resp.is_success)
        self.assertEqual(object_id, self.get_zip_name())
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, self.get_context())
        self.assertFalse(self.receipt_called)
        # check comments were not stored
        self.mock_datastore.commit_entity.assert_not_called()
