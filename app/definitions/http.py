from abc import ABC, abstractmethod
from typing import Protocol

import requests

from app.response import Response


class Http(Protocol):
    def post(
        self,
        domain: str,
        endpoint: str,
        json_data: str | None = None,
        params: dict[str, str] | None = None,
        files: dict[str, bytes] | None = None,
    ) -> requests.Response: ...


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
