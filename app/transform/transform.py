from app.definitions import SurveySubmission
from app.submission_type import requires_pck
from app.transform import image, index, pck, idbr, json

from app.transform.zip import create_zip


def transform(submission: SurveySubmission) -> bytes:
    files: dict[str, bytes] = {}

    # PCK
    if requires_pck(submission):
        files[f"EDC_QData/{pck.get_name(submission)}"] = pck.get_contents(submission)

    # Image
    image_name = image.get_name(submission)
    files[f"EDC_QImages/Images/{image_name}"] = image.get_image(submission)

    # Index
    files[f"EDC_QImages/Index/{index.get_name(submission)}"] = index.get_contents(submission, image_name)

    # IDBR Receipt
    files[f"EDC_QReceipts/{idbr.get_name(submission)}"] = idbr.get_contents(submission)

    # Original json
    files[f"EDC_QJson/{json.get_name(submission)}"] = json.get_contents(submission)

    return create_zip(files)
