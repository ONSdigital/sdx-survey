from app.definitions.period import PeriodBase, PeriodFormatError


class Period(PeriodBase):
    def __init__(self, period_id: str):
        self._period_id = period_id

        if len(period_id) == 6:
            pf = "YYYYMM"
        elif len(period_id) == 4:
            pf = "YYMM"
        elif len(period_id) == 2:
            pf = "YY"
        else:
            raise PeriodFormatError(f"Period in wrong format {period_id}")
        self._period_format = pf

    def get_format(self) -> str:
        return self._period_format

    def convert_to_format(self, new_format: str) -> str:
        period = self._period_id
        current_format = self._period_format

        symbols: dict[str, list[str]] = {"D": [], "M": [], "Y": []}

        for i in range(0, len(period)):
            k = current_format[i]
            if k not in symbols:
                raise PeriodFormatError(f"Period in wrong format {current_format}")
            symbols[k].append(period[i])

        if new_format.count("Y") == 4:
            if len(symbols["Y"]) == 2:
                symbols["Y"].insert(0, "0")
                symbols["Y"].insert(0, "2")
        elif new_format.count("Y") == 2:
            if len(symbols["Y"]) == 4:
                symbols["Y"].pop(0)
                symbols["Y"].pop(0)

        if new_format.count("M") == 2:
            if len(symbols["M"]) == 0:
                symbols["M"].append("1")
                symbols["M"].append("2")

        if new_format.count("D") == 2:
            if len(symbols["D"]) == 0:
                symbols["D"].append("0")
                symbols["D"].append("1")

        result = ""
        for f in new_format:
            result += symbols[f].pop(0)

        return result

    def convert_to_yyyymm(self) -> str:
        return self.convert_to_format("YYYYMM")

    def are_comparable(self, other) -> bool:
        if set(self._period_format) != set(other.get_format()):
            return False
        return True

    def __ge__(self, other):
        if not self.are_comparable(other):
            raise PeriodFormatError(f"Periods are not comparable {self._period_format} {other.get_format()}")

        return self.convert_to_yyyymm() >= other.convert_to_yyyymm()

    def __gt__(self, other):
        if not self.are_comparable(other):
            raise PeriodFormatError(f"Periods are not comparable {self._period_format} {other.get_format()}")

        return self.convert_to_yyyymm() > other.convert_to_yyyymm()

    def __le__(self, other):
        if not self.are_comparable(other):
            raise PeriodFormatError(f"Periods are not comparable {self._period_format} {other.get_format()}")

        return self.convert_to_yyyymm() <= other.convert_to_yyyymm()

    def __lt__(self, other):
        if not self.are_comparable(other):
            raise PeriodFormatError(f"Periods are not comparable {self._period_format} {other.get_format()}")

        return self.convert_to_yyyymm() < other.convert_to_yyyymm()
