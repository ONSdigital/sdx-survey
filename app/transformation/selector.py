from app.definitions.http import TransformPosterBase, ImagePosterBase
from app.definitions.survey_type import SurveyType
from app.definitions.transform import Transform
from app.transformation.transforms.adhoc import AdhocTransform
from app.transformation.transforms.feedback import FeedbackTransform
from app.transformation.transforms.idbr import IDBRTransform
from app.transformation.transforms.image import ImageTransform
from app.transformation.transforms.index import IndexTransform
from app.transformation.transforms.json import JsonTransform
from app.transformation.transforms.pck import PCKTransform
from app.transformation.transforms.spp import SPPTransform
from app.transformation.transforms.v1_json import V1JsonTransform


class TransformSelector:

    def __init__(self,
                 transform_poster: TransformPosterBase,
                 image_poster: ImagePosterBase,
                 ftp_path: str):

        pck_transform: Transform = PCKTransform(transform_poster)
        image_transform: Transform = ImageTransform(image_poster)
        index_transform: Transform = IndexTransform(ftp_path)
        idbr_transform: Transform = IDBRTransform()
        json_transform: Transform = JsonTransform()
        spp_transform: Transform = SPPTransform(transform_poster)
        feedback_transform: Transform = FeedbackTransform()
        v1_json_transform: Transform = V1JsonTransform()
        adhoc_transform: Transform = AdhocTransform()

        self._mapping: dict[SurveyType, list[Transform]] = {
            SurveyType.LEGACY: [pck_transform, image_transform, index_transform, idbr_transform],
            SurveyType.MATERIALS: [json_transform, image_transform, index_transform, idbr_transform],
            SurveyType.ENVIRONMENTAL: [v1_json_transform, image_transform, index_transform, idbr_transform],
            SurveyType.SPP: [spp_transform, image_transform, index_transform, idbr_transform],
            SurveyType.DAP: [v1_json_transform],
            SurveyType.FEEDBACK: [feedback_transform],
            SurveyType.ADHOC: [adhoc_transform]
        }

    def select(self, survey_type: SurveyType) -> list[Transform]:
        return self._mapping[survey_type]
