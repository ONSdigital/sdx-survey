from app.definitions import SurveySubmission
from app.submission_type import requires_pck, requires_transformed_image
from app.transform import image, index, pck, idbr, json

from app.transform.zip import create_zip
from json import loads as json_loads


def transform(submission: SurveySubmission) -> bytes:
    files: dict[str, bytes] = {}

    # PCK
    if requires_pck(submission):
        files[f"EDC_QData/{pck.get_name(submission)}"] = pck.get_contents(submission)

    # Image
    image_name = image.get_name(submission)
    if requires_transformed_image(submission):
        transformed_json = pck.get_contents(submission)
        transformed_submission: SurveySubmission = json_loads(transformed_json)
        image_bytes = image.get_image(transformed_submission)
    else:
        image_bytes = image.get_image(submission)
    files[f"EDC_QImages/Images/{image_name}"] = image_bytes

    # Remaining
    files[f"EDC_QImages/Index/{index.get_name(submission)}"] = index.get_contents(submission, image_name)
    files[f"EDC_QReceipts/{idbr.get_name(submission)}"] = idbr.get_contents(submission)
    files[f"EDC_QJson/{json.get_name(submission)}"] = json.get_contents(submission)

    return create_zip(files)
