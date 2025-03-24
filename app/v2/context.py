from typing import TypedDict
from enum import StrEnum


class SurveyType(StrEnum):
    DAP = "dap"
    LEGACY = "legacy"
    SPP = "spp"
    NS5 = "ns5"
    FEEDBACK = "feedback"
    SEFT = "seft"
    ADHOC = "adhoc"
    COMMENTS = "comments"


class Context(TypedDict):
    tx_id: str
    survey_type: SurveyType


class BusinessSurveyContext(Context):
    survey_id: str
    period_id: str
    ru_ref: str


class AdhocSurveyContext(Context):
    survey_id: str
    title: str
    label: str
