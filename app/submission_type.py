from enum import Enum


class SurveyType(Enum):
    BUSINESS = 1
    ADHOC = 2


class ResponseType(Enum):
    SURVEY = 1
    FEEDBACK = 2


class SchemaVersion(Enum):
    V1 = 1
    V2 = 2


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
