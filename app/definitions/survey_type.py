from enum import StrEnum


class SurveyType(StrEnum):
    DAP = "dap"
    LEGACY = "legacy"
    SPP = "spp"
    ENVIRONMENTAL = "environmental"
    MATERIALS = "materials"
    FEEDBACK = "feedback"
    ADHOC = "adhoc"
    DEXTA = "dexta"
