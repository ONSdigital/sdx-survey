from sdx_gcp.app import get_logger

from app import CONFIG
from app.response import Response, SurveyType, ResponseType, SchemaVersion, DeliverTarget
from app.v2.submission_type_v2 import ADHOC_SURVEY

"""
    This file defines a set of classifiers for the different submission types.
"""

logger = get_logger()

# list of survey ids that target only DAP
_DAP_SURVEYS = ["283", "738", "739", "740"]

# list of survey ids that target both DAP and Legacy
_HYBRID_SURVEYS = ["002", "007", "009", "023", "134", "147"]

# list of surveys that require a PCK file
_PCK_SURVEYS = [
    '009', '017', '019', '061', '066', '076', '073', '074', '127', '132', '134', '139', '144',
    '160', '165', '169', '171', '182', '183', '184', '185', '187', '202', '221', '228'
]

# surveys that need to remain v1 submissions
_V1_SURVEYS = ["283", "007", "009", "023", "134", "147"]

# surveys that currently only require a receipt (usually for testing purposes)
_RECEIPT_ONLY_SURVEYS = []

# json name change
_JSON_NAME_CHANGE = ["024", "068", "071", "194"]

# json transformation
_JSON_TRANSFORM = ["002"]

# responses that will use the v2 schema for messaging Nifi
_V2_NIFI_MESSAGE = ["002", "007", "009", "023", "068", "139", "228"]


def requires_v1_conversion(response: Response) -> bool:
    if response.get_response_type() == ResponseType.FEEDBACK:
        return False
    if response.get_schema_version() == SchemaVersion.V1:
        return False
    return response.get_survey_id() in _V1_SURVEYS


def requires_pck(response: Response) -> bool:
    return response.get_survey_id() in _PCK_SURVEYS


def requires_json_name_change(response: Response) -> bool:
    return response.get_survey_id() in _JSON_NAME_CHANGE


def requires_json_transform(response: Response) -> bool:
    return response.get_survey_id() in _JSON_TRANSFORM


def receipt_only_submission(response: Response) -> bool:
    return response.get_survey_id() in _RECEIPT_ONLY_SURVEYS


def get_deliver_target(response: Response) -> DeliverTarget:
    """
    Gets the DeliverTarget for this response

    The order of the following assertions is important as they
    are not necessarily mutually exclusive.
    E.g. A response could be both feedback and adhoc, but it
    is important that it is assigned a feedback delivery target.
    """
    if response.get_response_type() == ResponseType.FEEDBACK:
        return DeliverTarget.FEEDBACK

    if response.get_survey_type() == SurveyType.ADHOC:
        return DeliverTarget.DAP

    survey_id = response.get_survey_id()
    if survey_id in _DAP_SURVEYS:
        return DeliverTarget.DAP
    elif survey_id in _HYBRID_SURVEYS:
        return DeliverTarget.HYBRID
    else:
        return DeliverTarget.LEGACY


def is_v2_nifi_message_submission(response: Response) -> bool:
    """
    Returns True if this response is configured to use the v2 nifi message schema.
    """

    # DFTS-1053
    if response.get_response_type() == ResponseType.FEEDBACK:
        # Adhoc feedback is not yet ready for v2 message!
        if response.get_survey_type() == SurveyType.ADHOC:
            return False
        else:
            return True

    if response.get_survey_id() not in ADHOC_SURVEY:
        return True

    if CONFIG.PROJECT_ID == "ons-sdx-preprod" or CONFIG.PROJECT_ID == "ons-sdx-nifi":
        return response.get_survey_id() in _V2_NIFI_MESSAGE

    return False
