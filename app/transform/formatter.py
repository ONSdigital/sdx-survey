from datetime import datetime


def split_ru_ref(ru_ref: str) -> tuple[str, str]:
    new_ref: str = ru_ref[0:-1] if ru_ref[-1].isalpha() else ru_ref
    ru_check: str = ru_ref[-1] if ru_ref and ru_ref[-1].isalpha() else ""
    return new_ref, ru_check


def get_tx_code(tx_id: str):
    """Format the tx_id."""
    # tx_code is the first 16 digits of the tx_id without hyphens
    return "".join(tx_id.split("-"))[0:16]


def format_date(d: datetime, format_str: str):
    """convert a datetime to a different format."""
    return d.strftime(format_str)


def get_datetime(iso_8601_str: str) -> datetime:
    """
    Convert a string format datetime into a datetime
    """
    return datetime.fromisoformat(iso_8601_str)


def get_period(period: str) -> str:
    # ensure the period is 6 digits
    if len(period) == 2:
        period = "20" + period + "12"
    elif len(period) == 4:
        period = "20" + period

    return period
