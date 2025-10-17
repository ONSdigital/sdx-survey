from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from app.services.comments import CommentData
from tests.integration.test_base import TestBase


class TestDap(TestBase):
    def test_bics(self):
        self.set_survey_submission("283.0001.json")

        resp = self.client.post("/", json=self.envelope)

        expected_filename = "c37a3efa-593c-4bab-b49c-bee0613c4fb4.json"

        actual_files = self.get_zip_contents()

        # expected context
        expected_context: Context = {
            "tx_id": "c37a3efa-593c-4bab-b49c-bee0613c4fb4",
            "survey_type": SurveyType.DAP,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "283",
            "period_id": "201605",
            "ru_ref": "11842491738S",
        }

        expected_receipt = {"caseId": "846b8188-8235-4025-a5ef-5b98c693d6f1", "partyId": "UNKNOWN"}

        expected_comments: CommentData = {'additional': [],
                                          'boxes_selected': '',
                                          'comment': 'I am a 283 comment',
                                          'ru_ref': '11842491738S'}

        expected_kind = "283_201605"

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, self.get_context())
        self.assertEqual(expected_receipt, self.get_receipt())
        self.assertEqual(expected_comments, self.get_comment_data())
        self.assertEqual(expected_kind, self.get_comment_kind())
