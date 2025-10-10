import json
from typing import TypedDict, Optional, Protocol

from datetime import datetime
from string import ascii_lowercase
from cryptography.fernet import Fernet
from sdx_base.settings.service import SECRET

from app import get_logger
from app.definitions.comments import CommentsBase
from app.response import Response
from app.transformation.formatter import get_datetime

logger = get_logger()


class Comment:
    """Class to define a comment entity"""

    def __init__(self, transaction_id: str, kind: str, encrypted_data, submitted_time: datetime):
        self.transaction_id = transaction_id
        self.kind = kind
        self.encrypted_data = encrypted_data
        self.created = submitted_time


class AdditionalComment(TypedDict):
    qcode: str
    comment: Optional[str]


class CommentsSettings(Protocol):
    project_id: str
    sdx_comment_key: SECRET
    srm_receipt_topic_path: str


class CommentsWriter(Protocol):
    def commit_entity(self,
                      data: dict[str, str],
                      kind: str,
                      tx_id: str,
                      project_id: Optional[str] = None,
                      exclude_from_indexes: Optional[str] = None):
        ...



class CommentsService(CommentsBase):

    def __init__(self, settings: CommentsSettings, comments_writer: CommentsWriter):
        self._settings = settings
        self._comments_writer = comments_writer

    def store_comments(self, response: Response):
        """
        Extracts the comments from a survey submission and
        writes them to Google Datastore

        The comments are encrypted and stored along with
        useful metadata required for retrival.
        """

        transaction_id = response.get_tx_id()
        period = response.get_period()
        survey_id = response.get_survey_id()
        data = {"ru_ref": response.get_ru_ref(),
                "boxes_selected": self.get_boxes_selected(response),
                "comment": self.get_comment(response),
                "additional": self.get_additional_comments(response)}

        encrypted_data = self.encrypt_comment(data)
        kind = f'{survey_id}_{period}'
        submitted_time = get_datetime(response.get_submitted_at())

        comment = Comment(transaction_id=transaction_id,
                          kind=kind,
                          encrypted_data=encrypted_data,
                          submitted_time=submitted_time)

        self.commit_to_datastore(comment)


    def encrypt_comment(self, data: dict) -> str:
        logger.info('Encrypting comments')
        comment_str = json.dumps(data)
        f = Fernet(self._settings.sdx_comment_key)
        token = f.encrypt(comment_str.encode())
        return token.decode()


    def get_comment(self, response: Response) -> str:
        """
        Returns the respondent typed text from a submission.
        The qcode for this text will be different depending on the survey.
        """
        logger.info('Checking comment Q Codes')

        survey_id = response.get_survey_id()
        if survey_id == '187':
            return self.extract_comment(response, '500')
        elif survey_id == '134':
            return self.extract_comment(response, '300')
        elif survey_id == '002':
            return self.extract_berd_comment(response)
        elif survey_id == '221':
            return self.extract_bres_comment(response)
        else:
            return self.extract_comment(response, '146')


    def extract_comment(self, response: Response, qcode) -> str:
        logger.info('Extracting comments')
        return response.get_data().get(qcode)


    def get_additional_comments(self, response: Response) -> list[AdditionalComment]:
        logger.info('Getting additional comments')
        comments_list = []
        data = response.get_data()
        if response.get_survey_id() == '134':
            if '300w' in data:
                comments_list.append(self.get_additional(response, '300w'))
            if '300f' in data:
                comments_list.append(self.get_additional(response, '300f'))
            if '300m' in data:
                comments_list.append(self.get_additional(response, '300m'))
            if '300w4' in data:
                comments_list.append(self.get_additional(response, '300w4'))
            if '300w5' in data:
                comments_list.append(self.get_additional(response, '300w5'))
        return comments_list


    def get_additional(self, response: Response, qcode: str) -> AdditionalComment:
        logger.info('Getting additional')
        return {'qcode': qcode, "comment": response.get_data().get(qcode)}


    def get_boxes_selected(self, response: Response) -> str:
        logger.info('Getting all the selected boxes')
        boxes_selected = ''
        if response.get_survey_id() == '134':
            checkboxes = ['91w', '92w1', '92w2', '94w1', '94w2', '95w', '96w', '97w',
                          '91f', '92f1', '92f2', '94f1', '94f2', '95f', '96f', '97f',
                          '191m', '192m1', '192m2', '194m1', '194m2', '195m', '196m', '197m',
                          '191w4', '192w41', '192w42', '194w41', '194w42', '195w4', '196w4', '197w4',
                          '191w5', '192w51', '192w52', '194w51', '194w52', '195w5', '196w5', '197w5']
            for checkbox in checkboxes:
                if checkbox in response.get_data():
                    boxes_selected = boxes_selected + f"{checkbox}, "

        else:
            for key in ('146' + letter for letter in ascii_lowercase[0:]):
                if key in response.get_data().keys():
                    boxes_selected = boxes_selected + key + ' '

        return boxes_selected

    def commit_to_datastore(self, comment: Comment):
        """Write an instance of Comment to Google Datastore"""

        data = {
            "created": comment.created,
            "encrypted_data": comment.encrypted_data
        }
        self._comments_writer.commit_entity(data,
                                          kind=comment.kind,
                                          tx_id=comment.transaction_id,
                                          project_id=self._settings.project_id,
                                          exclude_from_indexes="encrypted_data")

    def extract_data_0_0_3_comment(self, response: Response, qcode: str) -> str:
        """
        Responses in data version 0.0.3 require matching the qcode
        with the answer id to be able to extract the comment.
        """
        try:
            if 'answer_codes' not in response.get_data():
                return self.extract_comment(response, qcode)

            answer_codes: list[dict[str, str]] = response.get_data()['answer_codes']
            answer_id = ""
            for answer_code in answer_codes:
                if answer_code["code"] == qcode:
                    answer_id = answer_code["answer_id"]

            if answer_id != "":
                answers: list[dict[str, str]] = response.get_data()['answers']
                for answer in answers:
                    if answer["answer_id"] == answer_id:
                        return answer["value"]
        except Exception as e:
            logger.error(str(e))

        return ""


    def extract_berd_comment(self, response: Response) -> str:
        return self.extract_data_0_0_3_comment(response, "712")


    def extract_bres_comment(self, response: Response) -> str:
        """
        Extract the comments for BRES

        BRES has multiple comment questions relating to changes in name
        and each address line. These are all concatenated into one comment.
        """
        comment = "Name:\n"
        comment += self.extract_data_0_0_3_comment(response, "9954")
        comment += "\n"
        comment += "Address:\n"
        for qcode in ["9982", "9981", "9980", "9979", "9978", "9977"]:
            c = self.extract_data_0_0_3_comment(response, qcode)
            if c != "":
                comment += c + "\n"

        return comment[:-1]
