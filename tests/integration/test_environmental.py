from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from tests.integration.test_base import TestBase, get_json


class TestEnvironmental(TestBase):

    def test_lcree(self):
        submission_json = get_json("007.0009.json")
        tx_id = submission_json["tx_id"]
        self.set_survey_submission(tx_id, submission_json)

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_json_filename = '007_837e9fe2eab84909.json'
        expected_image_filename = 'S837e9fe2eab84909_1.JPG'
        expected_index_filename = 'EDC_007_20210203_837e9fe2eab84909.csv'
        expected_receipt_filename = 'REC0302_837e9fe2eab84909.DAT'

        # actual files
        actual_files = self.get_zip_contents()

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.ENVIRONMENTAL,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "007",
            "period_id": "201605",
            "ru_ref": "15339216474W"
        }

        # actual context
        actual_context: Context = self.get_context()

        # expected_receipt
        expected_receipt = {
                'caseId': "4bc5a896-994f-4c5d-b592-9da04147378a",
                'partyId': "UNKNOWN"
            }

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
