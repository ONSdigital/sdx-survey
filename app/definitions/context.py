from typing import TypedDict, NotRequired

from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType


class Context(TypedDict):
    tx_id: str
    survey_type: SurveyType
    context_type: ContextType
    survey_id: str
    period_id: NotRequired[str]
    ru_ref: NotRequired[str]
