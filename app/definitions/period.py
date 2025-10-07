from abc import ABC, abstractmethod


class PeriodFormatError(Exception):
    pass


class PeriodBase(ABC):

    @abstractmethod
    def get_format(self) -> str:
        pass

    @abstractmethod
    def convert_to_format(self, new_format: str) -> str:
       pass

    @abstractmethod
    def convert_to_yyyymm(self) -> str:
        pass

    @abstractmethod
    def are_comparable(self, other) -> bool:
        pass
