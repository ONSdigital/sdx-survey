from abc import ABC, abstractmethod

from app.response import Response


class TransformPosterBase(ABC):

    @abstractmethod
    def call_transformer_pck(self, response: Response) -> bytes:
        pass

    @abstractmethod
    def call_transformer_spp(self, response: Response) -> bytes:
        pass


class ImagePosterBase(ABC):

    @abstractmethod
    def call_image(self, response: Response) -> bytes:
        pass