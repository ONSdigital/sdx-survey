from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from tests.integration.test_base import TestBase, get_json


class TestLegacy(TestBase):
    def test_mbs(self):
        submission_json = get_json("009.0106.json")
        tx_id = submission_json["tx_id"]
        self.set_survey_submission(tx_id, submission_json)

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_pck_filename = "009_bddbb41275ea43ce"
        expected_image_filename = "Sbddbb41275ea43ce_1.JPG"
        expected_index_filename = "EDC_009_20230118_bddbb41275ea43ce.csv"
        expected_receipt_filename = "REC1801_bddbb41275ea43ce.DAT"

        # actual files
        actual_files = self.get_zip_contents()

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.LEGACY,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "009",
            "period_id": "1605",
            "ru_ref": "12346789012A",
        }

        # actual context
        actual_context: Context = self.get_context()

        # expected_receipt
        expected_receipt = {"caseId": "8fc3eb0b-2dd7-4acd-a354-5d4f69503233", "partyId": "UNKNOWN"}

        # actual receipt
        actual_receipt = self.get_receipt()

        self.assertTrue(resp.is_success)
        self.assertEqual(self.pck_contents, actual_files[expected_pck_filename])
        self.assertEqual(self.image_contents, actual_files[expected_image_filename])
        self.assertTrue(expected_index_filename in actual_files)
        self.assertTrue(expected_receipt_filename in actual_files)
        self.assertEqual(4, len(actual_files))
        self.assertEqual(expected_context, actual_context)
        self.assertEqual(expected_receipt, actual_receipt)
        # check comments were stored
        self.mock_datastore.commit_entity.assert_called()
