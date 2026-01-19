from typing import Self

from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from app.services.comments import CommentData
from tests.integration.test_base import TestBase


class TestLegacy(TestBase):
    def test_mbs(self: Self):
        self.set_survey_submission("009.0106.json")
        tx_id = self.submission_json["tx_id"]

        resp = self.client.post("/", json=self.envelope)

        expected_pck_filename = "009_bddbb41275ea43ce"
        expected_image_filename = "Sbddbb41275ea43ce_1.JPG"
        expected_index_filename = "EDC_009_20230118_bddbb41275ea43ce.csv"
        expected_receipt_filename = "REC1801_bddbb41275ea43ce.DAT"

        actual_files = self.get_zip_contents()

        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.LEGACY,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "009",
            "period_id": "1605",
            "ru_ref": "12346789012A",
        }

        expected_receipt = {"caseId": "8fc3eb0b-2dd7-4acd-a354-5d4f69503233", "partyId": "UNKNOWN"}

        expected_comments: CommentData = {
            "ru_ref": "12346789012A",
            "boxes_selected": "",
            "comment": "I am a 009 comment",
            "additional": [],
        }

        expected_kind = "009_1605"

        self.assertTrue(resp.is_success)
        self.assertEqual(tx_id, self.get_zip_name())
        self.assertEqual(self.pck_contents, actual_files[expected_pck_filename])
        self.assertEqual(self.image_contents, actual_files[expected_image_filename])
        self.assertTrue(expected_index_filename in actual_files)
        self.assertTrue(expected_receipt_filename in actual_files)
        self.assertEqual(4, len(actual_files))
        self.assertEqual(expected_context, self.get_context())
        self.assertEqual(expected_receipt, self.get_receipt())
        self.assertEqual(expected_comments, self.get_comment_data())
        self.assertEqual(expected_comments, self.get_comment_data())
        self.assertEqual(expected_kind, self.get_comment_kind())
