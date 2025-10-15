import json
import unittest

from app.response import Response


class TestVersionReverter(unittest.TestCase):

    def test_json_template(self):
        data = {
            "case_id": "a7b21d95-8e4e-465a-9a9b-2caeefb96265",
            "tx_id": "006ac9de-c25d-4fb1-bc01-8369a0ca6d31",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "v2",
            "data_version": "0.0.1",
            "origin": "uk.gov.ons.edc.eq",
            "collection_exercise_sid": "e71b2cf8-c944-443a-8b62-f327358f49c2",
            "schema_name": "abs_1802",
            "flushed": False,
            "submitted_at": "2023-05-15T14:06:19+00:00",
            "launch_language_code": "en",
            "survey_metadata": {
                "survey_id": "202",
                "ref_p_end_date": "2016-05-31",
                "period_id": "201605",
                "user_id": "UNKNOWN",
                "ru_ref": "12346789012A",
                "ref_p_start_date": "2016-05-01",
                "trad_as": "ESSENTIAL ENTERPRISE LTD.",
                "ru_name": "ESSENTIAL ENTERPRISE LTD.",
                "form_type": "1802"
            },
            "data": {
                "9999": "Yes, I can report for this period",
                "399": "0",
                "80": "No",
                "450": "0",
                "403": "0",
                "420": "0",
                "400": "0",
                "500": "0",
                "599": "0",
                "600": "0",
                "699": "0",
                "163": "0",
                "164": "0",
                "15": "No",
                "16": "No",
                "9": "No",
                "146": "hello"
            },
            "started_at": "2023-05-15T14:04:29.047307+00:00",
            "submission_language_code": "en"
        }

        expected = {
            "case_id": "a7b21d95-8e4e-465a-9a9b-2caeefb96265",
            "tx_id": "006ac9de-c25d-4fb1-bc01-8369a0ca6d31",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "0.0.1",
            "origin": "uk.gov.ons.edc.eq",
            "survey_id": "202",
            "flushed": False,
            "submitted_at": "2023-05-15T14:06:19+00:00",
            "collection": {
                "exercise_sid": "e71b2cf8-c944-443a-8b62-f327358f49c2",
                "schema_name": "abs_1802",
                "period": "201605",
                "instrument_id": "1802"
            },
            "metadata": {
                "user_id": "UNKNOWN",
                "ru_ref": "12346789012A",
                "ref_period_start_date": "2016-05-01",
                "ref_period_end_date": "2016-05-31"
            },
            "launch_language_code": "en",
            "data": {
                "9999": "Yes, I can report for this period",
                "399": "0",
                "80": "No",
                "450": "0",
                "403": "0",
                "420": "0",
                "400": "0",
                "500": "0",
                "599": "0",
                "600": "0",
                "699": "0",
                "163": "0",
                "164": "0",
                "15": "No",
                "16": "No",
                "9": "No",
                "146": "hello"
            },
            "form_type": "1802",
            "started_at": "2023-05-15T14:04:29.047307+00:00",
            "submission_language_code": "en"
        }

        actual = Response(data, "006ac9de-c25d-4fb1-bc01-8369a0ca6d31").to_v1_json()
        expected = json.dumps(expected)

        self.assertEqual(expected, actual)

    def test_json_template_with_optional_missing(self):
        data = {
            "case_id": "a7b21d95-8e4e-465a-9a9b-2caeefb96265",
            "tx_id": "006ac9de-c25d-4fb1-bc01-8369a0ca6d31",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "v2",
            "data_version": "0.0.1",
            "collection_exercise_sid": "e71b2cf8-c944-443a-8b62-f327358f49c2",
            "schema_name": "abs_1802",
            "submitted_at": "2023-05-15T14:06:19+00:00",
            "launch_language_code": "en",
            "survey_metadata": {
                "survey_id": "202",
                "ref_p_end_date": "2016-05-31",
                "period_id": "201605",
                "user_id": "UNKNOWN",
                "ru_ref": "12346789012A",
                "ref_p_start_date": "2016-05-01",
                "trad_as": "ESSENTIAL ENTERPRISE LTD.",
                "ru_name": "ESSENTIAL ENTERPRISE LTD.",
                "form_type": "1802"
            },
            "data": {
                "9999": "Yes, I can report for this period",
                "399": "0",
                "80": "No",
                "450": "0",
                "403": "0",
                "420": "0",
                "400": "0",
                "500": "0",
                "599": "0",
                "600": "0",
                "699": "0",
                "163": "0",
                "164": "0",
                "15": "No",
                "16": "No",
                "9": "No",
                "146": "hello"
            },
            "started_at": "2023-05-15T14:04:29.047307+00:00",
            "submission_language_code": "en"
        }

        expected = {
            "case_id": "a7b21d95-8e4e-465a-9a9b-2caeefb96265",
            "tx_id": "006ac9de-c25d-4fb1-bc01-8369a0ca6d31",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "0.0.1",
            "origin": "",
            "survey_id": "202",
            "flushed": "",
            "submitted_at": "2023-05-15T14:06:19+00:00",
            "collection": {
                "exercise_sid": "e71b2cf8-c944-443a-8b62-f327358f49c2",
                "schema_name": "abs_1802",
                "period": "201605",
                "instrument_id": "1802"
            },
            "metadata": {
                "user_id": "UNKNOWN",
                "ru_ref": "12346789012A",
                "ref_period_start_date": "2016-05-01",
                "ref_period_end_date": "2016-05-31"
            },
            "launch_language_code": "en",
            "data": {
                "9999": "Yes, I can report for this period",
                "399": "0",
                "80": "No",
                "450": "0",
                "403": "0",
                "420": "0",
                "400": "0",
                "500": "0",
                "599": "0",
                "600": "0",
                "699": "0",
                "163": "0",
                "164": "0",
                "15": "No",
                "16": "No",
                "9": "No",
                "146": "hello"
            },
            "form_type": "1802",
            "started_at": "2023-05-15T14:04:29.047307+00:00",
            "submission_language_code": "en"
        }

        actual = Response(data, "006ac9de-c25d-4fb1-bc01-8369a0ca6d31").to_v1_json()
        expected = json.dumps(expected)

        self.assertEqual(expected, actual)
