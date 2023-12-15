from sdx_gcp.app import get_logger

from app.response import Response, SurveyType, ResponseType, SchemaVersion, DeliverTarget

"""
    This file defines a set of classifiers for the different submission types.
"""

logger = get_logger()

# list of survey ids that target only DAP
_DAP_SURVEYS = ["283", "738", "739"]

# list of survey ids that target both DAP and Legacy
_HYBRID_SURVEYS = ["002", "007", "009", "023", "134", "147"]

# list of surveys that require a PCK file
_PCK_SURVEYS = ['009', '017', '019', '073', '074', '127', '134', '139', '144', '160', '165', '169', '171',
                '182', '183', '184', '185', '187', '202', '228']

# surveys that still use SDX transform
_LEGACY_TRANSFORMER = ['002', '092']

# surveys that need to remain v1 submissions
_V1_SURVEYS = ["283", "007", "009", "023", "134", "147"]

# prepop surveys
_PREPOP_SURVEYS = ["068", "071"]

# json name change
_JSON_NAME_CHANGE = ["024", "194"]


def requires_v1_conversion(response: Response) -> bool:
    if response.get_response_type() == ResponseType.FEEDBACK:
        return False
    if response.get_schema_version() == SchemaVersion.V1:
        return False
    return response.get_survey_id() in _V1_SURVEYS


def requires_legacy_transform(response: Response) -> bool:
    return response.get_survey_id() in _LEGACY_TRANSFORMER


def requires_pck(response: Response) -> bool:
    return response.get_survey_id() in _PCK_SURVEYS


def requires_json_name_change(response: Response) -> bool:
    return response.get_survey_id() in _JSON_NAME_CHANGE


def prepop_submission(response: Response) -> bool:
    return response.get_survey_id() in _PREPOP_SURVEYS


def get_deliver_target(response: Response) -> DeliverTarget:
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
