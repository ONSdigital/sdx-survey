
def response_json_name(survey_id, tx_id):
	return "{0}_{1}.json".format(survey_id, _get_tx_code(tx_id))


def idbr_name(user_ts, tx_id):
	"""Generate the name of an IDBR file."""
	return "REC{0}_{1}.DAT".format(user_ts.strftime("%d%m"), _get_tx_code(tx_id))


def pck_name(survey_id, tx_id):
	"""Generate the name of a PCK file."""
	return f"{survey_id}_{_get_tx_code(tx_id)}"


def get_idbr(survey_id, ru_ref, ru_check, period):
	"""Write an IDBR file."""
	return _idbr_receipt(survey_id, ru_ref, ru_check, period)


def _idbr_receipt(survey_id, ru_ref, ru_check, period):
	"""Format a receipt in IDBR format."""
	# ensure the period is 6 digits
	if len(period) == 2:
		period = "20" + period + "12"
	elif len(period) == 4:
		period = "20" + period

	return "{0}:{1}:{2:03}:{3}".format(ru_ref, ru_check, int(survey_id), period)


def get_image_name(tx_id: str, i: int):
	return f"S{_get_tx_code(tx_id)}_{i}.JPG"


def get_index_name(survey_id: str, submission_date: str, tx_id: str):
	tx_code = _get_tx_code(tx_id)
	return "EDC_{0}_{1}_{2}.csv".format(survey_id, submission_date, tx_code)


def _get_tx_code(tx_id: str):
	"""Format the tx_id."""
	# tx_code is the first 16 digits of the tx_id without hyphens
	return "".join(tx_id.split("-"))[0:16]
