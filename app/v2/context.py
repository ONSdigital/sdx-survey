from typing import TypedDict, NotRequired

from app.definitions.v2_context_type import V2ContextType
from app.definitions.v2_survey_type import V2SurveyType


class Context(TypedDict):
    tx_id: str
    survey_type: V2SurveyType
    context_type: V2ContextType
    survey_id: str
    period_id: NotRequired[str]
    ru_ref: NotRequired[str]
