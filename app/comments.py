import json
from typing import TypedDict, Optional

from sdx_gcp.app import get_logger
from datetime import datetime
from string import ascii_lowercase
from cryptography.fernet import Fernet

from app import sdx_app, CONFIG
from app.response import Response

logger = get_logger()


def store_comments(response: Response):
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
            "boxes_selected": get_boxes_selected(response),
            "comment": get_comment(response),
            "additional": get_additional_comments(response)}

    encrypted_data = encrypt_comment(data)
    kind = f'{survey_id}_{period}'

    comment = Comment(transaction_id=transaction_id,
                      kind=kind,
                      encrypted_data=encrypted_data)

    commit_to_datastore(comment)


def encrypt_comment(data: dict) -> str:
    logger.info('Encrypting comments')
    comment_str = json.dumps(data)
    f = Fernet(CONFIG.ENCRYPT_COMMENT_KEY)
    token = f.encrypt(comment_str.encode())
    return token.decode()


def get_comment(response: Response) -> str:
    """
    Returns the respondent typed text from a submission.
    The qcode for this text will be different depending on the survey.
    """
    logger.info('Checking comment Q Codes')

    survey_id = response.get_survey_id()
    if survey_id == '187':
        return extract_comment(response, '500')
    elif survey_id == '134':
        return extract_comment(response, '300')
    elif survey_id == '002':
        return extract_berd_comment(response)
    else:
        return extract_comment(response, '146')


def extract_comment(response: Response, qcode) -> str:
    logger.info('Extracting comments')
    return response.get_data().get(qcode)


class AdditionalComment(TypedDict):
    qcode: str
    comment: Optional[str]


def get_additional_comments(response: Response) -> list[AdditionalComment]:
    logger.info('Getting additional comments')
    comments_list = []
    data = response.get_data()
    if response.get_survey_id() == '134':
        if '300w' in data:
            comments_list.append(get_additional(response, '300w'))
        if '300f' in data:
            comments_list.append(get_additional(response, '300f'))
        if '300m' in data:
            comments_list.append(get_additional(response, '300m'))
        if '300w4' in data:
            comments_list.append(get_additional(response, '300w4'))
        if '300w5' in data:
            comments_list.append(get_additional(response, '300w5'))
    return comments_list


def get_additional(response: Response, qcode: str) -> AdditionalComment:
    logger.info('Getting additional')
    return {'qcode': qcode, "comment": response.get_data().get(qcode)}


def get_boxes_selected(response: Response) -> str:
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


class Comment:
    """Class to define a comment entity"""

    def __init__(self, transaction_id, kind, encrypted_data):
        self.transaction_id = transaction_id
        self.kind = kind
        self.encrypted_data = encrypted_data
        self.created = datetime.now()


def commit_to_datastore(comment: Comment):
    """Write an instance of Comment to Google Datastore"""

    data = {
        "created": comment.created,
        "encrypted_data": comment.encrypted_data
    }
    sdx_app.datastore_write(data, comment.kind, comment.transaction_id, exclude_from_indexes="encrypted_data")


def extract_data_0_0_3_comment(response: Response, qcode: str) -> str:
    try:
        if 'answer_codes' not in response.get_data():
            return extract_comment(response, qcode)

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


def extract_berd_comment(response: Response) -> str:
    return extract_data_0_0_3_comment(response, "712")


def extract_bres_comment(response: Response) -> str:
    """
    Extract the comments for BRES

    BRES has multiple comment questions relating to changes in name
    and each address line. These are all concatenated into one comment.
    """
    comment = "Name:\n"
    comment += extract_data_0_0_3_comment(response, "9954")
    comment += "\n"
    comment += "Address:\n"
    for qcode in ["9982", "9981", "9980", "9979", "9978", "9977"]:
        c = extract_data_0_0_3_comment(response, qcode)
        if c != "":
            comment += c + "\n"

    return comment[:-1]
