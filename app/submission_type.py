from enum import Enum

# list of survey ids that target only DAP
_DAP_SURVEYS = ["283"]
# list of surveys that target DAP and Legacy
_HYBRID_SURVEYS = ["007", "023", "134", "147"]


class SurveyType(Enum):
    BUSINESS = 1
    ADHOC = 2


class ResponseType(Enum):
    SURVEY = 1
    FEEDBACK = 2


class SchemaVersion(Enum):
    V1 = 1
    V2 = 2


class DeliverTarget(Enum):
    LEGACY = 1
    DAP = 2
    HYBRID = 3
    FEEDBACK = 4


def get_response_type(survey_dict: dict) -> ResponseType:
    survey_type = survey_dict.get("type")
    if survey_type:
        if "feedback" in survey_dict.get("type"):
            return ResponseType.FEEDBACK
    return ResponseType.SURVEY


def get_survey_type(survey_dict: dict) -> SurveyType:
    channel = survey_dict.get("channel")
    if channel:
        if "RH" in survey_dict.get("channel"):
            return SurveyType.ADHOC
    return SurveyType.BUSINESS


def get_schema_version(survey_dict: dict) -> SchemaVersion:
    version = survey_dict.get("version")
    if version:
        if survey_dict.get("version") == "v2":
            return SchemaVersion.V2
    return SchemaVersion.V1


def get_deliver_target(survey_dict: dict) -> DeliverTarget:
    if get_response_type(survey_dict) == ResponseType.FEEDBACK:
        return DeliverTarget.FEEDBACK

    if get_survey_type(survey_dict) == SurveyType.ADHOC:
        return DeliverTarget.DAP

    if get_schema_version(survey_dict) == SchemaVersion.V2:
        survey_id = survey_dict['survey_metadata']['survey_id']
    else:
        survey_id = survey_dict['survey_id']

    if survey_id in _DAP_SURVEYS:
        return DeliverTarget.DAP
    elif survey_id in _HYBRID_SURVEYS:
        return DeliverTarget.HYBRID
    else:
        return DeliverTarget.LEGACY
