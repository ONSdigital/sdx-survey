from abc import ABC, abstractmethod

from app.definitions.submission import SurveySubmission


class DecryptionBase(ABC):
    @abstractmethod
    def decrypt_survey(self, payload: str) -> SurveySubmission:
        pass
