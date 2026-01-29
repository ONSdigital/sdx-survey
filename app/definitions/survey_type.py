from enum import StrEnum


class SurveyType(StrEnum):
    DAP = "dap"
    SPP = "spp"
    ENVIRONMENTAL = "environmental"
    MATERIALS = "materials"
    FEEDBACK = "feedback"
    ADHOC = "adhoc"
    DEXTA = "dexta"
    PCK_ONLY = "pck_only"
