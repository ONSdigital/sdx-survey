from typing import TypedDict, NotRequired

from app.definitions.context_type import V2ContextType
from app.definitions.survey_type import SurveyType


class Context(TypedDict):
    tx_id: str
    survey_type: SurveyType
    context_type: V2ContextType
    survey_id: str
    period_id: NotRequired[str]
    ru_ref: NotRequired[str]
