from app.definitions.transform import Transform
from app.definitions.transformer import TransformerBase
from app.response import Response
from app.transformation.transforms.feedback import FeedbackTransform
from app.transformation.transforms.idbr import IDBRTransform
from app.transformation.transforms.image import ImageTransform
from app.transformation.transforms.index import IndexTransform
from app.transformation.transforms.json import JsonTransform
from app.transformation.transforms.pck import PCKTransform
from app.transformation.transforms.spp import SPPTransform
from app.transformation.transforms.v1_json import V1JsonTransform
from app.transformation.zip import create_zip


class Transformer(TransformerBase):
    def __init__(self, transform_list: list[Transform]):
        self._transform_list = transform_list

    def create_zip(self, response: Response) -> bytes:
        files: dict[str, bytes] = {}

        for transform in self._transform_list:
            name = transform.get_file_name(response)
            content = transform.get_file_content(response)

            files[name] = content

        return create_zip(files)


class LegacyTransformer(Transformer):
    def __init__(self):
        transform_list = [PCKTransform(), ImageTransform(), IndexTransform(), IDBRTransform()]
        super().__init__(transform_list)


class MaterialsTransformer(Transformer):
    def __init__(self):
        transform_list = [JsonTransform(), ImageTransform(), IndexTransform(), IDBRTransform()]
        super().__init__(transform_list)


class SPPTransformer(Transformer):
    def __init__(self):
        transform_list = [SPPTransform(), ImageTransform(), IndexTransform(), IDBRTransform()]
        super().__init__(transform_list)


class DAPTransformer(Transformer):
    def __init__(self):
        transform_list = [V1JsonTransform()]
        super().__init__(transform_list)


class FeedbackTransformer(Transformer):
    def __init__(self):
        transform_list = [FeedbackTransform()]
        super().__init__(transform_list)


class EnvironmentalTransformer(Transformer):
    def __init__(self):
        transform_list = [V1JsonTransform(), ImageTransform(), IndexTransform(), IDBRTransform()]
        super().__init__(transform_list)
