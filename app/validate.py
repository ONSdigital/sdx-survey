from pathlib import Path
import jsonschema
import structlog

from app.errors import QuarantinableError

logger = structlog.get_logger()

path = Path("./schemas")
resolver = jsonschema.validators.RefResolver(
    base_uri=f"{path.resolve().as_uri()}/",
    referrer=True,
)

# A dict of dicts containing lists of form_types mapped to survey ids
KNOWN_SURVEYS = {
    "002": [
        "0001"
    ],
    "007": [
        "0010", "0009"
    ],
    "009": [
        "0106", "0111", "0117", "0123", "0158", "0161", "0167", "0173", "0201", "0202",
        "0203", "0204", "0205", "0216", "0251", "0253", "0255", "0817", "0823", "0867",
        "0873",
    ],
    "017": [
        "0001", "0002", "0003", "0004", "0005", "0006", "0007", "0008", "0009", "0010",
        "0011", "0012", "0013", "0014", "0033", "0034", "0051", "0052", "0057", "0058",
        "0061", "0070"
    ],
    "019": ["0018", "0019", "0020"],
    "023": ["0203", "0213", "0205", "0215", "0102", "0112"],
    "024": ["0002"],
    "073": ["0002"],
    "074": ["0002"],
    "092": ["0001"],
    "134": ["0005"],
    "139": ["0001"],
    "144": ["0001", "0002"],
    "147": ["0003", "0004"],
    "160": ["0002"],
    "165": ["0002"],
    "169": ["0003"],
    "171": ["0002", "0003"],
    "182": ["0006"],
    "183": ["0006"],
    "184": ["0006"],
    "185": ["0005"],
    "187": ["0001", "0002", "0051"],
    "194": ["0001"],
    "202": ["1802", "1804", "1808", "1810", "1812", "1814", "1818", "1820", "1824", "1826", "1862", "1864", "1874"],
    "228": ["0001", "0002"],
    "283": ["0001", "0002"]
}


def check_known_survey(survey_id: str, form_type: str):
    """Tests if a survey id is valid"""
    if survey_id not in KNOWN_SURVEYS:
        logger.error("Survey id is not known", survey_id=survey_id)
        raise ValueError(f"Invalid survey id: {survey_id}")

    if form_type not in KNOWN_SURVEYS[survey_id]:
        logger.error("form_type is not known", survey_id=survey_id, form_type=form_type)
        raise ValueError(f"Invalid form_type: {form_type}")


def validate(submission: dict) -> bool:
    """
    Validates every aspect of a survey submission in dictionary form.
    Returns True if valid or raises an appropriate exception if not.
    """

    try:
        json_data = submission

        logger.info("Validating json against schema")

        version = json_data.get("version")
        if version == "v2":

            jsonschema.validate(
                instance=json_data,
                schema={"$ref": "submission_v2.json"},
                resolver=resolver,
            )

        else:

            jsonschema.validate(
                instance=json_data,
                schema={"$ref": "submission_v1.json"},
                resolver=resolver,
            )

            survey_id = json_data.get("survey_id")
            form_type = json_data.get("collection", {}).get("instrument_id")

            try:
                check_known_survey(survey_id, form_type)
            except ValueError:
                raise QuarantinableError(f"Unsupported survey_id and/or form_type '{survey_id}:{form_type}'")

    except jsonschema.ValidationError as e:
        logger.error("Client error", error=e.message)
        raise QuarantinableError(e.message)

    except Exception as e:
        logger.error("Server error", error=e)
        raise QuarantinableError(e)

    logger.info(f"Validation successful")
    return True
