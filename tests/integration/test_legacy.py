from typing import Self

from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from app.services.comments import CommentData
from tests.integration.test_base import TestBase


class TestLegacy(TestBase):

    def test_des(self: Self):
        self.set_survey_submission("187.0001.json")

        resp = self.client.post("/", json=self.envelope)

        expected_pck_filename = "187_d63e2bba29a346c0"
        expected_image_filename = "Sd63e2bba29a346c0_1.JPG"
        expected_index_filename = "EDC_187_20221221_d63e2bba29a346c0.csv"
        expected_receipt_filename = "REC2112_d63e2bba29a346c0.DAT"

        actual_files = self.get_zip_contents()

        expected_context: Context = {
            "tx_id": "d63e2bba-29a3-46c0-8e7e-6ef1986ff5c9",
            "survey_type": SurveyType.LEGACY,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "187",
            "period_id": "201605",
            "ru_ref": "12346789012A",
        }

        expected_receipt = {"caseId": "da18ae74-afe5-4748-a578-459f7bc645a3", "partyId": "UNKNOWN"}

        expected_comments: CommentData = {
            "ru_ref": "12346789012A",
            "boxes_selected": "",
            "comment": "I am a 187 comment",
            "additional": [],
        }

        expected_kind = "187_201605"

        self.assertTrue(resp.is_success)
        self.assertEqual(self.pck_contents, actual_files[expected_pck_filename])
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
