import unittest
from unittest.mock import patch, Mock

from app.response import Response
from app.transform.transform import transform
from sdx_gcp.errors import DataError


class TestTransform(unittest.TestCase):

    def setUp(self):

        self.tx_id = "befa5444-749f-407a-b3a2-19f1d1c7324b"
        self.submission = {
            "case_id": "34d30023-ee05-4f7c-b5a5-12639b4f045e",
            "tx_id": "befa5444-749f-407a-b3a2-19f1d1c7324b",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "v2",
            "data_version": "0.0.1",
            "origin": "uk.gov.ons.edc.eq",
            "collection_exercise_sid": "e666daad-cdda-4dac-812f-fa9b9361258f",
            "schema_name": "test_1801",
            "flushed": False,
            "submitted_at": "2023-09-29T09:30:21+00:00",
            "launch_language_code": "en",
            "survey_metadata": {
                "survey_id": "202",
                "user_id": "UNKNOWN",
                "ru_ref": "12346789012A",
                "ru_name": "ESSENTIAL ENTERPRISE LTD.",
                "trad_as": "ESSENTIAL ENTERPRISE LTD.",
                "period_id": "201605",
                "ref_p_start_date": "2016-05-01",
                "ref_p_end_date": "2016-05-31",
                "form_type": "1801"
            },
            "data": {'001': 'hi'},
            "started_at": "2023-09-29T09:07:10.640686+00:00",
            "submission_language_code": "en"
        }

    @patch("app.transform.transform.create_zip")
    @patch("app.transform.transform.json")
    @patch("app.transform.transform.idbr")
    @patch("app.transform.transform.index")
    @patch("app.transform.transform.image")
    @patch("app.transform.transform.pck")
    def test_transform(self, mock_pck, mock_image, mock_index, mock_idbr, mock_json, mock_create_zip: Mock):

        mock_pck.get_contents.return_value = "pck_contents"
        mock_pck.get_name.return_value = "pck_name"

        mock_image.get_image.return_value = "image_contents"
        mock_image.get_name.return_value = "image_name"

        mock_index.get_contents.return_value = "index_contents"
        mock_index.get_name.return_value = "index_name"

        mock_idbr.get_contents.return_value = "idbr_contents"
        mock_idbr.get_name.return_value = "idbr_name"

        mock_json.get_contents.return_value = "json_contents"
        mock_json.get_name.return_value = "json_name"

        expected_files = {
            "EDC_QData/pck_name": "pck_contents",
            "EDC_QImages/Images/image_name": "image_contents",
            "EDC_QImages/Index/index_name": "index_contents",
            "EDC_QReceipts/idbr_name": "idbr_contents",
            "EDC_QJson/json_name": "json_contents",
        }

        transform(Response(self.submission, self.tx_id))

        mock_create_zip.assert_called_with(
            expected_files
        )

    @patch("app.transform.transform.create_zip")
    @patch("app.transform.transform.json")
    @patch("app.transform.transform.idbr")
    @patch("app.transform.transform.index")
    @patch("app.transform.transform.image")
    @patch("app.transform.transform.pck")
    def test_transform_with_no_survey_metadata(self, mock_pck, mock_image, mock_index, mock_idbr, mock_json, mock_create_zip: Mock):

        mock_pck.get_contents.return_value = "pck_contents"
        mock_pck.get_name.return_value = "pck_name"

        mock_image.get_image.return_value = "image_contents"
        mock_image.get_name.return_value = "image_name"

        mock_index.get_contents.return_value = "index_contents"
        mock_index.get_name.return_value = "index_name"

        mock_idbr.get_contents.return_value = "idbr_contents"
        mock_idbr.get_name.return_value = "idbr_name"

        mock_json.get_contents.return_value = "json_contents"
        mock_json.get_name.return_value = "json_name"

        # Remove the survey metadata
        del self.submission["survey_metadata"]

        with self.assertRaises(DataError):
            transform(Response(self.submission, self.tx_id))
