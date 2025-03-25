import json
import unittest
from unittest import mock
from unittest.mock import patch
from cryptography.fernet import Fernet

from app.comments import get_comment, get_additional_comments, get_boxes_selected, encrypt_comment, store_comments, \
    Comment, commit_to_datastore, extract_berd_comment, extract_bres_comment
from app.definitions.submission import SurveySubmission
from app.response import Response


class StoreCommentsTest(unittest.TestCase):
    test_survey = {
        "tx_id": "1027a13a-c253-4e9d-9e78-d0f0cfdd3988",
        "type": "uk.gov.ons.edc.eq:surveyresponse",
        "case_id": "bb9eaf11-a729-40b5-8d17-d112e018c0d5",
        "origin": "uk.gov.ons.edc.eq",
        "started_at": "2019-04-01T14:00:24.224709",
        "submitted_at": "2019-04-01T14:10:26.933601",
        "version": "v2",
        "collection_exercise_sid": "664dbdf4-02fb-4d68-b0cf-7f7402df00e5",
        "flushed": False,
        "survey_metadata": {
            "survey_id": "017",
            "form_type": "0011",
            "period_id": "201904",
            "ref_p_end_date": "2018-11-29",
            "ref_p_start_date": "2019-04-01",
            "ru_ref": "15162882666F",
            "user_id": "UNKNOWN",
            "ru_name": "Test Name"
        },
        "data": {
            "15": "No",
            "119": "150",
            "120": "152",
            "144": "200",
            "145": "124",
            "146": "This is a comment"
        }
    }

    @patch('app.comments.extract_comment')
    def test_get_comment_187(self, extract_comment):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '187'
        test_data['type'] = 'uk.gov.ons.edc.eq:feedback'

        data = Response(test_data, tx_id)
        get_comment(data)
        extract_comment.assert_called_with(data, "500")

    def test_extract_berd_comment(self):
        comment = "My Comment!"
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '002'
        test_data['data'] = {
            "answers": [
                {
                    "answer_id": "answerbd37d516-40be-4b5d-a657-823eb7c12e39",
                    "value": comment
                }
            ],
            "lists": [],
            "answer_codes": [
                {
                    "answer_id": "answerbd37d516-40be-4b5d-a657-823eb7c12e39",
                    "code": "712"
                }
            ]
        }

        self.assertEqual(comment, extract_berd_comment(Response(test_data, tx_id)))

    def test_extract_berd_comment_short_form(self):
        comment = "My Comment!"
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '002'
        test_data["data"] = {
            "123": "answer1",
            "712": comment
        }

        self.assertEqual(comment, extract_berd_comment(Response(test_data, tx_id)))

    def test_extract_bres_comment(self):
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '221'
        test_data['data'] = {
            "answers": [
                {"answer_id": "answerccd2c97c-28cb-460c-8f76-3d9f04aa98d6",
                 "value": "No, the business name is not correct"},
                {"answer_id": "answerca3136ef-d9ef-4bb8-8496-840dc1ac46c6",
                 "value": "corrected business name"},
                {"answer_id": "answera74a8052-0257-4dc4-83a0-598ce7bedb81",
                 "value": "No, the business address is not correct"},
                {"answer_id": "answerfaf14e92-e81b-4759-801f-8c6a1623020f",
                 "value": "address line1"},
                {"answer_id": "answercdade785-1566-414c-be8c-c228bfa24e2d",
                 "value": "address line2"},
                {"answer_id": "answerbe073353-2972-4f21-8773-3a43decb6e34",
                 "value": "AB12 3CD"}
            ],
            "lists": [
                {"items": ["aGlfLb", "sZqslY"],
                 "name": "local-units"}
            ],
            "answer_codes": [
                {"answer_id": "answerccd2c97c-28cb-460c-8f76-3d9f04aa98d6", "code": "9955"},
                {"answer_id": "answerca3136ef-d9ef-4bb8-8496-840dc1ac46c6", "code": "9954"},
                {"answer_id": "answera74a8052-0257-4dc4-83a0-598ce7bedb81", "code": "9953"},
                {"answer_id": "answerfaf14e92-e81b-4759-801f-8c6a1623020f", "code": "9982"},
                {"answer_id": "answercdade785-1566-414c-be8c-c228bfa24e2d", "code": "9981"},
                {"answer_id": "answerbe073353-2972-4f21-8773-3a43decb6e34", "code": "9977"}
            ]
        }

        expected = "Name:\ncorrected business name\nAddress:\naddress line1\naddress line2\nAB12 3CD"

        self.assertEqual(expected, extract_bres_comment(Response(test_data, tx_id)))

    def test_get_comment(self):
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '187'
        test_data['type'] = 'uk.gov.ons.edc.eq:feedback'
        test_data["data"] = {
            "500": "Im the 500 comment",
            "300": "Im the 300 comment",
            "146": "Im the 146 comment",
        }

        self.assertEqual(get_comment(Response(test_data, tx_id)), 'Im the 500 comment')
        test_data['survey_metadata']['survey_id'] = '134'
        self.assertEqual(get_comment(Response(test_data, tx_id)), 'Im the 300 comment')
        test_data['survey_metadata']['survey_id'] = '017'
        self.assertEqual(get_comment(Response(test_data, tx_id)), 'Im the 146 comment')

    def test_get_additional_comments(self):
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '134'
        test_data['type'] = 'uk.gov.ons.edc.eq:feedback'
        test_data["data"] = {
            "300w": "300w",
            "300m": "300m",
            "300w5": "300w5"
        }

        self.assertEqual(get_additional_comments(Response(test_data, tx_id)),
                         [{'qcode': '300w', "comment": '300w'},
                          {'qcode': '300m', "comment": '300m'},
                          {'qcode': '300w5', "comment": '300w5'}])

    def test_get_additional_comments_2(self):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '134'
        test_data['type'] = 'uk.gov.ons.edc.eq:feedback'
        test_data["data"] = {
            "300f": "hello",
            "300w4": "bye"
        }

        self.assertEqual(
            get_additional_comments(Response(test_data, tx_id)),
            [
                {'qcode': '300f', "comment": 'hello'},
                {'qcode': '300w4', "comment": 'bye'}
            ]
        )

    def test_get_additional_comments_none(self):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '134'
        test_data['type'] = 'uk.gov.ons.edc.eq:feedback'
        test_data["data"] = {
            "300a": "300w",
            "300b": "300m",
            "300c": "300w5"
        }

        self.assertEqual(get_additional_comments(Response(test_data, tx_id)), [])

    def test_get_boxes_selected(self):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '134'
        test_data['type'] = 'uk.gov.ons.edc.eq:feedback'
        test_data["data"] = {
            "91w": "Yes",
            "94w2": "Yes",
            "192w42": "Yes",
            "197w4": "Yes"
        }

        self.assertEqual("91w, 94w2, 192w42, 197w4, ", get_boxes_selected(Response(test_data, tx_id)))

    def test_get_boxes_selected_2(self):
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '009'
        test_data['type'] = 'uk.gov.ons.edc.eq:feedback'
        test_data["data"] = {
            "146a": "Yes"
        }

        self.assertEqual("146a ", get_boxes_selected(Response(test_data, tx_id)))

    def test_get_boxes_selected_none(self):
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_survey
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '134'
        test_data['type'] = 'uk.gov.ons.edc.eq:feedback'
        test_data["data"] = {
            "91w123": "Yes",
            "94w2123": "Yes",
            "192w42123": "Yes",
            "197w4123": "Yes"
        }

        self.assertEqual(get_boxes_selected(Response(test_data, tx_id)), "")

    @mock.patch('app.comments.CONFIG')
    def test_encryption_comments(self, mock_config):
        key = "E3rjFT2i9ALcvc99Pe3YqjIGrzm3LdMsCXc8nUaOEbc="
        mock_config.ENCRYPT_COMMENT_KEY = key

        test_data = {'additional': [{'comment': 'Pipe mania', 'qcode': '300w'},
                                    {'comment': 'Gas leak', 'qcode': '300f'},
                                    {'comment': 'copper pipe', 'qcode': '300m'},
                                    {'comment': 'solder joint', 'qcode': '300w4'},
                                    {'comment': 'drill hole', 'qcode': '300w5'}],
                     'boxes_selected': '91w, 95w, 96w, 97w, 91f, 95f, 96f, 97f, 191m, 195m, 196m, '
                                       '197m, 191w4, 195w4, 196w4, 197w4, 191w5, 195w5, 196w5, '
                                       '197w5, ',
                     'comment': 'flux clean',
                     'ru_ref': '12346789012A'
                     }
        encrypted_data = encrypt_comment(test_data)
        self.assertEqual(decrypt_comment(encrypted_data, key), test_data)

    @mock.patch('app.comments.CONFIG')
    @mock.patch('app.comments.commit_to_datastore')
    def test_store_comments_valid(self, mock_datastore, mock_config):
        key = "E3rjFT2i9ALcvc99Pe3YqjIGrzm3LdMsCXc8nUaOEbc="
        mock_config.ENCRYPT_COMMENT_KEY = key
        store_comments(Response(self.test_survey, "123"))
        mock_datastore.assert_called()

    @mock.patch('app.comments.sdx_app')
    def test_commmit_to_datastore(self, mock_app):
        comment = Comment("123", "009_2020", b'my data')
        commit_to_datastore(comment)
        mock_app.datastore_write.assert_called()


def decrypt_comment(comment_token: str, key: str) -> dict:
    f = Fernet(key)
    comment_bytes = f.decrypt(comment_token.encode())
    return json.loads(comment_bytes.decode())
