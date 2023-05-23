# change version: v2 to version: 0.0.1

# remove data version

# create collection object

# add collection_exercise_sid to collection object

# add schema_name to collection object

# remove flushed attribute

# move survey_id into outside object

# move period_id to collection object as period

# move user_id from survey_metadata to meta_data object

# move ru_ref from survey_metadata to meta_data object

# move ref_p_start_date from survey_metadata to metadata as ref_period_start_date

# move ref_p_end_date from survey_metadata to metadata as ref_period_end_date

# move form_type from survey_metadata into outside object

# move form_type from survey_metadata into collection object as instrument_id
from typing import Dict

from app.submission_type import get_field


class VersionReverter:

    def revert_data_to_v1(self, submission: Dict):
        v1_template = {
            "case_id": get_field(submission, "case_id"),
            "tx_id": get_field(submission, "tx_id"),
            "type": get_field(submission, "type"),
            "version": get_field(submission, "data_version"),
            "origin": get_field(submission, "origin"),
            "survey_id": get_field(submission, "survey_metadata", "survey_id"),
            "flushed": get_field(submission, "flushed"),
            "submitted_at": get_field(submission, "submitted_at"),
            "collection": {
                "exercise_sid": get_field(submission, "collection_exercise_sid"),
                "schema_name": get_field(submission, "schema_name"),
                "period": get_field(submission, "survey_metadata", "period_id"),
                "instrument_id": get_field(submission, "survey_metadata", "form_type")
            },
            "metadata": {
                "user_id": get_field(submission, "survey_metadata", "user_id"),
                "ru_ref": get_field(submission, "survey_metadata", "ru_ref"),
                "ref_period_start_date": get_field(submission, "survey_metadata", "ref_p_start_date"),
                "ref_period_end_date": get_field(submission, "survey_metadata", "ref_p_end_date")
            },
            "launch_language_code": get_field(submission, "launch_language_code"),
            "data": get_field(submission, "data"),
            "form_type": get_field(submission, "survey_metadata", "form_type"),
            "started_at": get_field(submission, "started_at"),
            "submission_language_code": get_field(submission, "submission_language_code")
        }

        return v1_template
