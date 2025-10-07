import unittest

from app.services.period import Period, PeriodFormatError


class ComparePeriodTests(unittest.TestCase):

    def test_incompatible_formats_YY_YYMM(self):
        p1 = Period("25")
        p2 = Period("2503")
        with self.assertRaises(PeriodFormatError):
            x = p1 > p2
            print(x)

    def test_incompatible_formats_YY_YYYYMM(self):
        p1 = Period("25")
        p2 = Period("202503")
        with self.assertRaises(PeriodFormatError):
            x = p1 > p2
            print(x)

    def test_compare_yy(self):
        p1 = Period("25")
        p2 = Period("24")
        p3 = Period("25")
        self.assertTrue(p1 > p2)
        self.assertTrue(p1 >= p3)
        self.assertTrue(p2 < p3)

    def test_compare_yymm(self):
        p1 = Period("2504")
        p2 = Period("2503")
        p3 = Period("2405")
        self.assertTrue(p1 > p2)
        self.assertTrue(p1 > p3)
        self.assertTrue(p3 <= p2)

    def test_compare_yyyymm(self):
        p1 = Period("202504")
        p2 = Period("202503")
        p3 = Period("202405")
        self.assertTrue(p1 > p2)
        self.assertTrue(p1 > p3)
        self.assertTrue(p3 <= p2)

    def test_compare_yyyymm_to_yymm(self):
        p1 = Period("202504")
        p2 = Period("2503")
        p3 = Period("2408")
        self.assertTrue(p1 > p2)
        self.assertTrue(p1 > p3)
        self.assertTrue(p2 <= p1)
        self.assertTrue(p3 <= p1)


class GetYYYYMMPeriodTests(unittest.TestCase):

    def test_yy_to_yyyymm(self):
        p1 = Period("25")
        actual = p1.convert_to_yyyymm()
        expected = "202512"
        self.assertEqual(expected, actual)

    def test_yymm_to_yyyymm(self):
        p1 = Period("2503")
        actual = p1.convert_to_yyyymm()
        expected = "202503"
        self.assertEqual(expected, actual)

    def test_yyyymm_to_yyyymm(self):
        p1 = Period("202503")
        actual = p1.convert_to_yyyymm()
        expected = "202503"
        self.assertEqual(expected, actual)
