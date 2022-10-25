from app.errors import QuarantinableError
from app.validate import validate, check_known_survey

import unittest
import json


responseTestDataMap = {
    "submission": "original/submission.json",
    "feedback": "original/feedback.json",
    "survey_v1_001": "payload_v1/surveyresponse_0_0_1.json",
    "feedback_v1_001": "payload_v1/feedback_0_0_1.json"
}


def get_data(name: str) -> dict:
    file = responseTestDataMap.get(name)
    if not file:
        raise ValueError
    path = f'tests/submissions/{file}'
    with open(path) as f:
        data = json.load(f)
    return data


class TestValidateService(unittest.TestCase):

    def assertInvalid(self, data: dict):
        with self.assertRaises(QuarantinableError):
            validate(data)

    def assertValid(self, data: dict):
        try:
            self.assertTrue(validate(data))
        except QuarantinableError as e:
            self.fail(str(e))

    def test_validates_submission(self):
        m = get_data('submission')
        self.assertValid(m)

    def test_validates_feedback(self):
        m = get_data('feedback')
        self.assertValid(m)

    def test_validates_eqv3_feedback(self):
        m = get_data('feedback_v1_001')
        self.assertValid(m)

    def test_mwss_valid(self):
        survey = get_data('submission')
        survey['survey_id'] = "134"
        survey['collection']['instrument_id'] = "0005"
        self.assertValid(survey)

    def test_mbs_valid(self):
        survey = get_data('submission')
        survey['survey_id'] = "009"
        survey['collection']['instrument_id'] = "0255"
        self.assertValid(survey)

    def test_epe_valid(self):
        survey = get_data('submission')
        survey['survey_id'] = "147"

        survey['collection']['instrument_id'] = "0003"
        self.assertValid(survey)

        survey['collection']['instrument_id'] = "0004"
        self.assertValid(survey)

    def test_qcas_valid(self):
        survey = get_data('submission')
        survey['survey_id'] = "019"

        survey['collection']['instrument_id'] = "0018"
        self.assertValid(survey)

        survey['collection']['instrument_id'] = "0019"
        self.assertValid(survey)

        survey['collection']['instrument_id'] = "0020"
        self.assertValid(survey)

        survey['collection']['instrument_id'] = "0021"
        self.assertInvalid(survey)

    def test_rsi_metadata(self):
        for inst_id in ["0102", "0112", "0203", "0205", "0213", "0215"]:
            with self.subTest(inst_id=inst_id):
                survey = get_data('submission')
                survey["survey_id"] = "023"
                survey["collection"]["instrument_id"] = inst_id
                survey["metadata"]["ref_period_start_date"] = "2016-04-01"
                survey["metadata"]["ref_period_end_date"] = "2016-10-31"
                self.assertValid(survey)

    def test_unknown_survey_id(self):
        with self.assertRaises(ValueError):
            check_known_survey("300", "")

    def test_unknown_formtype(self):
        with self.assertRaises(ValueError):
            check_known_survey("134", "0006")

    def test_known_survey_id_and_formtype(self):
        check_known_survey("134", "0005")

    def test_unknown_version_invalid(self):
        unknown_version = get_data('submission')
        unknown_version['version'] = "0.0.3"

        self.assertInvalid(unknown_version)

    def test_unknown_survey_invalid(self):
        unknown_survey = get_data('submission')
        unknown_survey['survey_id'] = "025"

        self.assertInvalid(unknown_survey)

    def test_blank_survey_invalid(self):
        unknown_survey = get_data('submission')
        unknown_survey['survey_id'] = ""

        self.assertInvalid(unknown_survey)

    def test_missing_survey_invalid(self):
        unknown_survey = get_data('submission')
        del unknown_survey['survey_id']

        self.assertInvalid(unknown_survey)

    def test_unknown_instrument_invalid(self):
        unknown_instrument = get_data('submission')
        unknown_instrument['collection']['instrument_id'] = "999"

        self.assertInvalid(unknown_instrument)

    def test_known_instrument_wrong_survey_invalid(self):
        # RSI survey_id with Census instrument_id
        known_instrument = get_data('submission')
        known_instrument['collection']['instrument_id'] = "household"

        self.assertInvalid(known_instrument)

    def test_known_instrument_correct_survey_valid(self):
        # RSI survey_id with RSI instrument_id
        known_instrument = get_data('submission')
        known_instrument['collection']['instrument_id'] = "0213"

        self.assertValid(known_instrument)

    def test_empty_data_invalid(self):
        empty_data = get_data('submission')
        empty_data['data'] = ""

        self.assertInvalid(empty_data)

    def test_feedback_empty_data_invalid(self):
        empty_data = get_data('feedback')
        empty_data['data'] = ""

        self.assertInvalid(empty_data)

    def test_string_data_invalid(self):
        data = "abcd"

        self.assertRaises(QuarantinableError, validate, data)

    def test_no_data(self):
        data = None

        self.assertInvalid(data)

    def test_non_guid_tx_id_invalid(self):
        wrong_tx = get_data('submission')
        wrong_tx['tx_id'] = "999"

        self.assertInvalid(wrong_tx)

        # Last character missing
        wrong_tx['tx_id'] = "f81d4fae-7dec-11d0-a765-00a0c91e6bf"

        self.assertInvalid(wrong_tx)

    def test_missing_tx_id_is_invalid(self):
        message = get_data('submission')
        del message['tx_id']

        self.assertInvalid(message)

    def test_flushed_not_boolean_fails(self):
        message = get_data('submission')
        message['flushed'] = ''

        self.assertInvalid(message)

    def test_flushed_key_missing_fails(self):
        message = get_data('submission')
        message.pop('flushed')

        self.assertInvalid(message)

    def test_case_id_and_case_ref_passes(self):
        message = get_data('submission')
        self.assertValid(message)

    def test_case_id_not_str_fails(self):
        message = get_data('submission')
        message['case_id'] = {}

        self.assertInvalid(message)

    def test_validate_type_none_is_quarantined(self):
        survey = get_data('submission')
        del survey["type"]
        with self.assertRaises(QuarantinableError):
            validate(survey)

    def test_validate_meta_none_is_quarantined(self):
        survey = get_data('submission')
        del survey["metadata"]
        with self.assertRaises(QuarantinableError):
            validate(survey)

    def test_not_known_survey(self):
        survey = get_data('submission')
        survey["survey_id"] = "567"
        with self.assertRaises(QuarantinableError):
            validate(survey)

    def test_not_known_survey_id(self):
        survey = get_data('submission')
        survey["survey_id"] = "567"
        with self.assertRaises(QuarantinableError):
            validate(survey)

    def test_allow_case_type(self):
        survey = get_data('submission')
        survey['case_type'] = "HH"
        self.assertValid(survey)

    def test_allow_all_eq_v3_fields(self):
        survey = get_data('submission')
        survey['collection']['schema_name'] = "mbs_1704"
        survey['metadata']['ref_period_start_date'] = "2016-05-01"
        survey['metadata']['ref_period_end_date'] = "2016-05-31"
        survey['launch_language_code'] = "en"
        survey['submission_language_code'] = "en"
        survey['form_type'] = "0167"
        survey['region_code'] = "GB-ENG"
        survey['case_ref'] = "1000000000000001"
        survey['case_type'] = "HH"
        survey['channel'] = "RAS"

        self.assertValid(survey)

    def test_exception_is_descriptive_for_missing_survey_id(self):
        survey = get_data('submission')
        del survey["survey_id"]
        try:
            validate(survey)
        except QuarantinableError as e:
            self.assertEqual("'survey_id' is a required property", str(e))
