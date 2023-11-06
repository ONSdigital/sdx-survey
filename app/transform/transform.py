from app.definitions import SurveySubmission
from app.transform import image, index, pck, idbr, json

from app.transform.zip import create_zip


def transform(submission: SurveySubmission) -> bytes:
    files: dict[str, bytes] = {}

    image_name = image.get_name(submission)

    files[f"EDC_QData/{pck.get_name(submission)}"] = pck.get_contents(submission)
    files[f"EDC_QImages/Images/{image_name}"] = image.get_image(submission)
    files[f"EDC_QImages/Index/{index.get_name(submission)}"] = index.get_contents(submission, image_name)
    files[f"EDC_QReceipts/{idbr.get_name(submission)}"] = idbr.get_contents(submission)
    files[f"EDC_QJson/{json.get_name(submission)}"] = json.get_contents(submission)

    return create_zip(files)
