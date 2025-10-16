import json
import unittest
from typing import Optional, Final

from cryptography.fernet import Fernet
from sdx_base.settings.service import SECRET

from app.definitions.submission import SurveySubmission
from app.response import Response
from app.services.comments import CommentsSettings, CommentsService, CommentData

COMMENT_KEY: Final[str] = "Pk_eTrrXIaiEv62A6w5qwerYCxR4060Xo1j5pJO_J2c="


def decrypt_comment(comment_token: str) -> dict:
    f = Fernet(COMMENT_KEY)
    comment_bytes = f.decrypt(comment_token.encode())
    return json.loads(comment_bytes.decode())


class MockCommentsWriter:

    def __init__(self):
        self._data: dict[str, str] = {}
        self._kind: str = ""

    def commit_entity(self,
                      data: dict[str, str],
                      kind: str,
                      tx_id: str,
                      project_id: Optional[str] = None,
                      exclude_from_indexes: Optional[str] = None):
        self._data = data
        self._kind = kind

    def get_comment_data(self) -> dict[str, str]:
        return decrypt_comment(self._data["encrypted_data"])

    def get_kind(self) -> str:
        return self._kind


class MockSettings:

    def __init__(self):
        self.project_id: str = "ons-sdx-sandbox"
        self.sdx_comment_key: SECRET = COMMENT_KEY
        self.srm_receipt_topic_path: str = 'projects/ons-sdx-sandbox/topics/srm-receipt-topic'


class StoreCommentsTest(unittest.TestCase):

    def setUp(self):
        self.comments_writer: MockCommentsWriter = MockCommentsWriter()
        self.comments_settings: CommentsSettings = MockSettings()
        self.comments_service = CommentsService(self.comments_settings, self.comments_writer)

        self.test_submission: SurveySubmission = {
            "tx_id": "1027a13a-c253-4e9d-9e78-d0f0cfdd3988",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "case_id": "bb9eaf11-a729-40b5-8d17-d112e018c0d5",
            "origin": "uk.gov.ons.edc.eq",
            "started_at": "2019-04-01T14:00:24.224709",
            "submitted_at": "2019-04-01T14:10:26.933601",
            "version": "v2",
            "collection_exercise_sid": "664dbdf4-02fb-4d68-b0cf-7f7402df00e5",
            "flushed": False,
            "data_version": "0.0.1",
            "launch_language_code": "en",
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

    def test_get_comment_from_146(self):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        test_data: SurveySubmission = self.test_submission
        test_data['tx_id'] = tx_id

        self.comments_service.store_comments(Response(self.test_submission))

        expected: CommentData = {
            'ru_ref': '15162882666F',
            'boxes_selected': '',
            'comment': 'This is a comment',
            'additional': []
        }

        actual = self.comments_writer.get_comment_data()
        self.assertEqual(expected, actual)
        self.assertEqual("017_201904", self.comments_writer.get_kind())

    def test_extract_berd_comment(self):
        comment = "My BERD Comment!"
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_submission
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

        self.comments_service.store_comments(Response(test_data))

        expected: CommentData = {
            'ru_ref': '15162882666F',
            'boxes_selected': '',
            'comment': 'My BERD Comment!',
            'additional': []
        }

        actual = self.comments_writer.get_comment_data()
        self.assertEqual(expected, actual)
        self.assertEqual("002_201904", self.comments_writer.get_kind())

    def test_extract_berd_comment_short_form(self):
        comment = "My short BERD Comment!"
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_submission
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '002'
        test_data["data"] = {
            "123": "answer1",
            "712": comment
        }

        self.comments_service.store_comments(Response(test_data))

        expected: CommentData = {
            'ru_ref': '15162882666F',
            'boxes_selected': '',
            'comment': 'My short BERD Comment!',
            'additional': []
        }

        actual = self.comments_writer.get_comment_data()
        self.assertEqual(expected, actual)
        self.assertEqual("002_201904", self.comments_writer.get_kind())

    def test_get_des_comments(self):
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_submission
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '187'
        test_data["data"] = {
            "500": "Im the des comment",
            "300": "Im the mwss comment",
            "146": "Im the wrong comment",
        }

        self.comments_service.store_comments(Response(test_data))

        expected: CommentData = {
            'ru_ref': '15162882666F',
            'boxes_selected': '',
            'comment': "Im the des comment",
            'additional': []
        }

        actual = self.comments_writer.get_comment_data()
        self.assertEqual(expected, actual)
        self.assertEqual("187_201904", self.comments_writer.get_kind())

    def test_get_mwss_comments(self):
            tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
            test_data: SurveySubmission = self.test_submission
            test_data['tx_id'] = tx_id
            test_data['survey_metadata']['survey_id'] = '134'
            test_data["data"] = {
                "500": "Im the des comment",
                "300": "Im the mwss comment",
                "146": "Im the wrong comment",
            }

            self.comments_service.store_comments(Response(test_data))

            expected: CommentData = {
                'ru_ref': '15162882666F',
                'boxes_selected': '',
                'comment': "Im the mwss comment",
                'additional': []
            }

            actual = self.comments_writer.get_comment_data()
            self.assertEqual(expected, actual)
            self.assertEqual("134_201904", self.comments_writer.get_kind())

    def test_get_additional_comments(self):
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_submission
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '134'
        test_data["data"] = {
            "300": "Im the mwss main comment",
            "300w": "300w",
            "300m": "300m",
            "300w5": "300w5"
        }

        self.comments_service.store_comments(Response(test_data))

        expected: CommentData = {
            'ru_ref': '15162882666F',
            'boxes_selected': '',
            'comment': "Im the mwss main comment",
            'additional':  [{'qcode': '300w', "comment": '300w'},
                          {'qcode': '300m', "comment": '300m'},
                          {'qcode': '300w5', "comment": '300w5'}]
        }

        actual = self.comments_writer.get_comment_data()
        self.assertEqual(expected, actual)
        self.assertEqual("134_201904", self.comments_writer.get_kind())

    def test_get_additional_comments_2(self):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        test_data: SurveySubmission = self.test_submission
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '134'
        test_data['type'] = 'uk.gov.ons.edc.eq:feedback'
        test_data["data"] = {
            "300f": "hello",
            "300w4": "bye"
        }

        self.comments_service.store_comments(Response(test_data))

        expected: CommentData = {
            'ru_ref': '15162882666F',
            'boxes_selected': '',
            'comment': None,
            'additional': [
                {'qcode': '300f', "comment": 'hello'},
                {'qcode': '300w4', "comment": 'bye'}
            ]
        }

        actual = self.comments_writer.get_comment_data()
        self.assertEqual(expected, actual)
        self.assertEqual("134_201904", self.comments_writer.get_kind())


    def test_get_additional_comments_none(self):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        test_data: SurveySubmission = self.test_submission
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '134'
        test_data["data"] = {
            "300a": "300w",
            "300b": "300m",
            "300c": "300w5"
        }

        self.comments_service.store_comments(Response(test_data))

        expected: CommentData = {
            'ru_ref': '15162882666F',
            'boxes_selected': '',
            'comment': None,
            'additional': []
        }

        actual = self.comments_writer.get_comment_data()
        self.assertEqual(expected, actual)

    def test_get_boxes_selected(self):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        test_data: SurveySubmission = self.test_submission
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '134'
        test_data["data"] = {
            "91w": "Yes",
            "94w2": "Yes",
            "192w42": "Yes",
            "197w4": "Yes"
        }

        self.comments_service.store_comments(Response(test_data))

        expected: CommentData = {
            'ru_ref': '15162882666F',
            'boxes_selected': "91w, 94w2, 192w42, 197w4, ",
            'comment': None,
            'additional': []
        }

        actual = self.comments_writer.get_comment_data()
        self.assertEqual(expected, actual)
#
    def test_get_boxes_selected_2(self):
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_submission
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '009'
        test_data["data"] = {
            "146a": "Yes"
        }

        self.comments_service.store_comments(Response(test_data))

        expected: CommentData = {
            'ru_ref': '15162882666F',
            'boxes_selected': "146a ",
            'comment': None,
            'additional': []
        }

        actual = self.comments_writer.get_comment_data()
        self.assertEqual(expected, actual)

    def test_get_boxes_selected_none(self):
        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        test_data: SurveySubmission = self.test_submission
        test_data['tx_id'] = tx_id
        test_data['survey_metadata']['survey_id'] = '134'
        test_data["data"] = {
            "91w123": "Yes",
            "94w2123": "Yes",
            "192w42123": "Yes",
            "197w4123": "Yes"
        }

        self.comments_service.store_comments(Response(test_data))

        expected: CommentData = {
            'ru_ref': '15162882666F',
            'boxes_selected': "",
            'comment': None,
            'additional': []
        }

        actual = self.comments_writer.get_comment_data()
        self.assertEqual(expected, actual)

# def test_extract_bres_comment(self):
#         tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
#         test_data: SurveySubmission = self.test_submission
#         test_data['tx_id'] = tx_id
#         test_data['survey_metadata']['survey_id'] = '221'
#         test_data['data'] = {
#             "answers": [
#                 {"answer_id": "answerccd2c97c-28cb-460c-8f76-3d9f04aa98d6",
#                  "value": "No, the business name is not correct"},
#                 {"answer_id": "answerca3136ef-d9ef-4bb8-8496-840dc1ac46c6",
#                  "value": "corrected business name"},
#                 {"answer_id": "answera74a8052-0257-4dc4-83a0-598ce7bedb81",
#                  "value": "No, the business address is not correct"},
#                 {"answer_id": "answerfaf14e92-e81b-4759-801f-8c6a1623020f",
#                  "value": "address line1"},
#                 {"answer_id": "answercdade785-1566-414c-be8c-c228bfa24e2d",
#                  "value": "address line2"},
#                 {"answer_id": "answerbe073353-2972-4f21-8773-3a43decb6e34",
#                  "value": "AB12 3CD"}
#             ],
#             "lists": [
#                 {"items": ["aGlfLb", "sZqslY"],
#                  "name": "local-units"}
#             ],
#             "answer_codes": [
#                 {"answer_id": "answerccd2c97c-28cb-460c-8f76-3d9f04aa98d6", "code": "9955"},
#                 {"answer_id": "answerca3136ef-d9ef-4bb8-8496-840dc1ac46c6", "code": "9954"},
#                 {"answer_id": "answera74a8052-0257-4dc4-83a0-598ce7bedb81", "code": "9953"},
#                 {"answer_id": "answerfaf14e92-e81b-4759-801f-8c6a1623020f", "code": "9982"},
#                 {"answer_id": "answercdade785-1566-414c-be8c-c228bfa24e2d", "code": "9981"},
#                 {"answer_id": "answerbe073353-2972-4f21-8773-3a43decb6e34", "code": "9977"}
#             ]
#         }
#
#         self.comments_service.store_comments(Response(test_data))
#
#         expected: CommentData = {
#             'ru_ref': '15162882666F',
#             'boxes_selected': '',
#             'comment': "Name:\ncorrected business name\nAddress:\naddress line1\naddress line2\nAB12 3CD",
#             'additional': []
#         }
#
#         actual = self.comments_writer.get_comment_data()
#         self.assertEqual(expected, actual)
#         self.assertEqual("221_201904", self.comments_writer.get_kind())
