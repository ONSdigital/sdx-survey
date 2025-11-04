from typing import TypedDict, NotRequired, Any

SurveyData = dict[str, str | list[Any]]


class BusinessSurveyMetadata(TypedDict):
    ru_name: str
    user_id: str
    period_id: str
    form_type: str
    ru_ref: str
    survey_id: str

    case_ref: NotRequired[str]
    case_type: NotRequired[str]
    display_address: NotRequired[str]
    employment_date: NotRequired[str]  # ISO_8601 date
    period_str: NotRequired[str]
    ref_p_start_date: NotRequired[str]  # ISO_8601 date
    ref_p_end_date: NotRequired[str]  # ISO_8601 date
    trad_as: NotRequired[str]
    sds_dataset_id: NotRequired[str]


class AdhocSurveyMetadata(TypedDict):
    survey_id: str
    qid: str
    PORTAL_ID: str
    PARTICIPANT_WINDOW_ID: str

    case_ref: NotRequired[str]
    BLOOD_TEST_BARCODE: NotRequired[str]
    SWAB_TEST_BARCODE: NotRequired[str]
    PARTICIPANT_ID: NotRequired[str]
    TEST_QUESTIONS: NotRequired[str]
    COLLEX_OPEN_DATE: NotRequired[str]
    COLLEX_CLOSE_DATE: NotRequired[str]
    FIRST_NAME: NotRequired[str]
    WINDOW_START_DATE: NotRequired[str]
    WINDOW_CLOSE_DATE: NotRequired[str]


class SurveySubmission(TypedDict):
    tx_id: str
    type: str
    version: str
    data_version: str
    origin: str
    flushed: bool
    submitted_at: str
    launch_language_code: str
    collection_exercise_sid: str
    case_id: str
    survey_metadata: BusinessSurveyMetadata | AdhocSurveyMetadata
    data: SurveyData

    channel: NotRequired[str]
    region_code: NotRequired[str]
    schema_name: NotRequired[str]
    schema_url: NotRequired[str]
    started_at: NotRequired[str]
    submission_language_code: NotRequired[str]
