from app.definitions import SurveySubmission
from app.transform import image, index, pck, idbr, json

from app.transform.zip import create_zip


def transform(submission: SurveySubmission) -> bytes:
    files = {}

    image_name = image.get_name(submission)

    files[pck.get_name(submission)] = pck.get_contents(submission)
    files[image_name] = image.get_image(submission)
    files[index.get_name(submission)] = index.get_contents(submission, image_name)
    files[idbr.get_name(submission)] = idbr.get_contents(submission)
    files[json.get_name(submission)] = json.get_contents(submission)

    return create_zip(files)
