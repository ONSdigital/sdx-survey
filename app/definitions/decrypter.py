from abc import ABC, abstractmethod
from typing import Any


class DecryptionBase(ABC):

    @abstractmethod
    def decrypt_survey(self, payload: str) -> dict[str, Any]:
        pass
