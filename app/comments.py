import json
import structlog

from datetime import datetime
from string import ascii_lowercase
from cryptography.fernet import Fernet
from google.cloud import datastore

from app import CONFIG
from app.errors import QuarantinableError
from app.submission_type import get_tx_id, get_period, get_survey_id, get_ru_ref

logger = structlog.get_logger()


def store_comments(submission: dict):
    """
    Extracts the comments from a survey submission and
    writes them to Google Datastore

    The comments are encrypted and stored along with
    useful metadata required for retrival.
    """

    transaction_id = get_tx_id(submission)
    period = get_period(submission)
    survey_id = get_survey_id(submission)
    data = {"ru_ref": get_ru_ref(submission),
            "boxes_selected": get_boxes_selected(submission),
            "comment": get_comment(submission),
            "additional": get_additional_comments(submission)}

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


def get_comment(submission: dict) -> list:
    """
    Returns the respondent typed text from a submission.
    The qcode for this text will be different depending on the survey.
    """
    logger.info('Checking comment Q Codes')

    survey_id = get_survey_id(submission)
    if survey_id == '187':
        return extract_comment(submission, '500')
    elif survey_id == '134':
        return extract_comment(submission, '300')
    else:
        return extract_comment(submission, '146')


def extract_comment(submission, qcode):
    logger.info('Extracting comments')
    return submission['data'].get(qcode)


def get_additional_comments(submission):
    logger.info('Getting additional comments')
    comments_list = []
    if get_survey_id(submission) == '134':
        if '300w' in submission['data']:
            comments_list.append(get_additional(submission, '300w'))
        if '300f' in submission['data']:
            comments_list.append(get_additional(submission, '300f'))
        if '300m' in submission['data']:
            comments_list.append(get_additional(submission, '300m'))
        if '300w4' in submission['data']:
            comments_list.append(get_additional(submission, '300w4'))
        if '300w5' in submission['data']:
            comments_list.append(get_additional(submission, '300w5'))
    return comments_list


def get_additional(submission, qcode):
    logger.info('Getting additional')
    return {'qcode': qcode, "comment": submission['data'].get(qcode)}


def get_boxes_selected(submission):
    logger.info('Getting all the selected boxes')
    boxes_selected = ''
    if get_survey_id(submission) == '134':
        checkboxes = ['91w', '92w1', '92w2', '94w1', '94w2', '95w', '96w', '97w',
                      '91f', '92f1', '92f2', '94f1', '94f2', '95f', '96f', '97f',
                      '191m', '192m1', '192m2', '194m1', '194m2', '195m', '196m', '197m',
                      '191w4', '192w41', '192w42', '194w41', '194w42', '195w4', '196w4', '197w4',
                      '191w5', '192w51', '192w52', '194w51', '194w52', '195w5', '196w5', '197w5']
        for checkbox in checkboxes:
            if checkbox in submission['data']:
                boxes_selected = boxes_selected + f"{checkbox}, "

    else:
        for key in ('146' + letter for letter in ascii_lowercase[0:]):
            if key in submission['data'].keys():
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

    try:
        logger.info(f'Storing comments in Datastore', kind=comment.kind)
        logger.info(f'Size of comment encrypted_data: {len(comment.encrypted_data)} bytes')
        entity_key = CONFIG.DATASTORE_CLIENT.key(comment.kind, comment.transaction_id)
        entity = datastore.Entity(key=entity_key, exclude_from_indexes=("encrypted_data",))
        entity.update(
            {
                "created": comment.created,
                "encrypted_data": comment.encrypted_data
            }
        )
        datastore.Client().put(entity)
    except ValueError as e:
        raise QuarantinableError(e)
