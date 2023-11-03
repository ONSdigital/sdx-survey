from datetime import datetime, timezone, date

import arrow


def pck_name(survey_id, tx_id):
    """Generate the name of a PCK file."""
    return f"{survey_id}_{get_tx_code(tx_id)}"


def get_image_name(tx_id: str, i: int):
    return f"S{get_tx_code(tx_id)}_{i}.JPG"


def get_index_name(survey_id: str, submission_date: str, tx_id: str):
    tx_code = get_tx_code(tx_id)
    return "EDC_{0}_{1}_{2}.csv".format(survey_id, submission_date, tx_code)


def split_ru_ref(ru_ref: str) -> tuple[str, str]:
    new_ref: str = ru_ref[0:-1] if ru_ref[-1].isalpha() else ru_ref
    ru_check: str = ru_ref[-1] if ru_ref and ru_ref[-1].isalpha() else ""
    return new_ref, ru_check


def get_tx_code(tx_id: str):
    """Format the tx_id."""
    # tx_code is the first 16 digits of the tx_id without hyphens
    return "".join(tx_id.split("-"))[0:16]


def format_date(value, style='long'):
    """convert a datetime to a different format."""

    timezone = 'Europe/London'
    if style == 'short':
        return arrow.get(value).to(timezone).format("YYYYMMDD")

    return arrow.get(value).to(timezone).format("DD/MM/YYYY HH:mm:ss")


def get_datetime(text: str) -> datetime | date | None:
    """Parse a text field for a date or timestamp.

    Date and time formats vary across surveys.
    This method reads those formats.

    :param str text: The date or timestamp value.
    :rtype: Python date or datetime.

    """

    cls = datetime

    if text.endswith("Z"):
        return cls.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )

    try:
        return cls.strptime(text, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        pass

    try:
        return cls.strptime(text, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        pass

    try:
        return cls.strptime(text.partition(".")[0], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass

    try:
        return cls.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        pass

    try:
        return cls.strptime(text, "%d/%m/%Y").date()
    except ValueError:
        pass

    try:
        return cls.strptime(text + "01", "%Y%m%d").date()
    except ValueError:
        pass

    return None
