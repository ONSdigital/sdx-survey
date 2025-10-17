from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from tests.integration.test_base import TestBase, get_json


class TestMaterials(TestBase):
    def test_qfs(self):
        submission_json = get_json("024.0002.json")
        tx_id = submission_json["tx_id"]
        self.set_survey_submission(tx_id, submission_json)

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_json_filename = "024_08449838140_201605.json"
        expected_image_filename = "S0d21ffe7dcb04d4e_1.JPG"
        expected_index_filename = "EDC_024_20220315_0d21ffe7dcb04d4e.csv"
        expected_receipt_filename = "REC1503_0d21ffe7dcb04d4e.DAT"

        # actual files
        actual_files = self.get_zip_contents()

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.MATERIALS,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "024",
            "period_id": "201605",
            "ru_ref": "08449838140O",
        }

        # actual context
        actual_context: Context = self.get_context()

        # expected_receipt
        expected_receipt = {"caseId": "c81d352b-b936-4f03-b5b7-07c6d370050d", "partyId": "UNKNOWN"}

        # actual receipt
        actual_receipt = self.get_receipt()

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_json_filename in actual_files)
        self.assertEqual(self.image_contents, actual_files[expected_image_filename])
        self.assertTrue(expected_index_filename in actual_files)
        self.assertTrue(expected_receipt_filename in actual_files)
        self.assertEqual(4, len(actual_files))
        self.assertEqual(expected_context, actual_context)
        self.assertEqual(expected_receipt, actual_receipt)
        # check comments were stored
        self.mock_datastore.commit_entity.assert_called()
