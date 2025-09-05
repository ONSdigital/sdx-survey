from enum import StrEnum


class V2SurveyType(StrEnum):
    DAP = "dap"
    LEGACY = "legacy"
    SPP = "spp"
    ENVIRONMENTAL = "environmental"
    MATERIALS = "materials"
    FEEDBACK = "feedback"
    ADHOC = "adhoc"
