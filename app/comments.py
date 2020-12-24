from datetime import datetime
from string import ascii_lowercase
from google.cloud import datastore

from app import PROJECT_ID
from app.encryption import encrypt_comment

datastore_client = datastore.Client(project=PROJECT_ID)
exclude_from_index = ('encrypted_data', 'period', 'survey_id')


def store_comments(survey_dict: dict):
    transaction_id = survey_dict["tx_id"]
    period = survey_dict["collection"]["period"]
    survey_id = survey_dict["survey_id"]
    data = {"ru_ref": survey_dict["metadata"]["ru_ref"],
            "boxes_selected": get_boxes_selected(survey_dict),
            "comment": get_comment(survey_dict),
            "additional": get_additional_comments(survey_dict)}
    encrypted_data = encrypt_comment(data)

    comment = Comment(transaction_id=transaction_id,
                      period=period,
                      survey_id=survey_id,
                      encrypted_data=encrypted_data)

    commit_to_datastore(comment)


def get_comment(submission: dict) -> list:
    """Returns the respondent typed text from a submission.  The qcode for this text will be different depending
    on the survey
    """
    if submission['survey_id'] == '187':
        return extract_comment(submission, '500')
    elif submission['survey_id'] == '134':
        return extract_comment(submission, '300')
    else:
        return extract_comment(submission, '146')


def extract_comment(submission, qcode):
    return submission['data'].get(qcode)


def get_additional_comments(submission):
    comments_list = []
    if submission['survey_id'] == '134':
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
    return {'qcode': qcode, "comment": submission['data'].get(qcode)}


def get_boxes_selected(submission):
    boxes_selected = ''
    if submission['survey_id'] == '134':
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
            if key in submission.keys():
                boxes_selected = boxes_selected + key + ' '

    return boxes_selected


class Comment:
    def __init__(self, transaction_id, survey_id, period, encrypted_data):
        self.transaction_id = transaction_id
        self.survey_id = survey_id
        self.period = period
        self.encrypted_data = encrypted_data
        self.created = datetime.now()


def commit_to_datastore(comment):
    try:
        entity_key = datastore_client.key('Comment', comment.transaction_id)
        entity = datastore.Entity(key=entity_key, exclude_from_indexes=exclude_from_index)
        entity.update(
            {
                "survey_id": comment.survey_id,
                "period": comment.period,
                "created": comment.created,
                "encrypted_data": comment.encrypted_data
            }
        )
        return datastore.Client().put(entity)
    except ValueError as error:
        print(error)
