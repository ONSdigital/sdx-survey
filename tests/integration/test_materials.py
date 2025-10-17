from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from app.services.comments import CommentData
from tests.integration.test_base import TestBase


class TestMaterials(TestBase):
    def test_qfs(self):
        self.set_survey_submission("024.0002.json")

        resp = self.client.post("/", json=self.envelope)

        expected_json_filename = "024_08449838140_201605.json"
        expected_image_filename = "S0d21ffe7dcb04d4e_1.JPG"
        expected_index_filename = "EDC_024_20220315_0d21ffe7dcb04d4e.csv"
        expected_receipt_filename = "REC1503_0d21ffe7dcb04d4e.DAT"

        actual_files = self.get_zip_contents()

        expected_context: Context = {
            "tx_id": "0d21ffe7-dcb0-4d4e-b66e-095cd2e58d7a",
            "survey_type": SurveyType.MATERIALS,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "024",
            "period_id": "201605",
            "ru_ref": "08449838140O",
        }

        expected_receipt = {"caseId": "c81d352b-b936-4f03-b5b7-07c6d370050d", "partyId": "UNKNOWN"}

        expected_comments: CommentData = {
            "ru_ref": "08449838140O",
            "boxes_selected": "",
            "comment": "Fuel is getting expensive!",
            "additional": [],
        }

        expected_kind = "024_201605"

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_json_filename in actual_files)
        self.assertEqual(self.image_contents, actual_files[expected_image_filename])
        self.assertTrue(expected_index_filename in actual_files)
        self.assertTrue(expected_receipt_filename in actual_files)
        self.assertEqual(4, len(actual_files))
        self.assertEqual(expected_context, self.get_context())
        self.assertEqual(expected_receipt, self.get_receipt())
        self.assertEqual(expected_comments, self.get_comment_data())
        self.assertEqual(expected_kind, self.get_comment_kind())
