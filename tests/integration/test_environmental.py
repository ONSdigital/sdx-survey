from typing import Self

from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from app.services.comments import CommentData
from tests.integration.test_base import TestBase


class TestEnvironmental(TestBase):
    def test_lcree(self: Self):
        self.set_survey_submission("007.0009.json")
        tx_id = self.submission_json["tx_id"]

        resp = self.client.post("/", json=self.envelope)

        expected_json_filename = "007_837e9fe2eab84909.json"
        expected_image_filename = "S837e9fe2eab84909_1.JPG"
        expected_index_filename = "EDC_007_20210203_837e9fe2eab84909.csv"
        expected_receipt_filename = "REC0302_837e9fe2eab84909.DAT"

        actual_files = self.get_zip_contents()

        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.ENVIRONMENTAL,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "007",
            "period_id": "201605",
            "ru_ref": "15339216474W",
        }

        expected_receipt = {"caseId": "4bc5a896-994f-4c5d-b592-9da04147378a", "partyId": "UNKNOWN"}

        expected_comments: CommentData = {
            "ru_ref": "15339216474W",
            "boxes_selected": "",
            "comment": None,
            "additional": [],
        }

        expected_kind = "007_201605"

        self.assertTrue(resp.is_success)
        self.assertEqual(tx_id, self.get_zip_name())
        self.assertTrue(expected_json_filename in actual_files)
        self.assertEqual(self.image_contents, actual_files[expected_image_filename])
        self.assertTrue(expected_index_filename in actual_files)
        self.assertTrue(expected_receipt_filename in actual_files)
        self.assertEqual(4, len(actual_files))
        self.assertEqual(expected_context, self.get_context())
        self.assertEqual(expected_receipt, self.get_receipt())
        self.assertEqual(expected_comments, self.get_comment_data())
        self.assertEqual(expected_kind, self.get_comment_kind())
