import datetime
import unittest

from app.transformation.formatter import get_datetime


class TestFormatter(unittest.TestCase):
    def test_get_datetime(self):
        input_time = "2019-04-01T14:10:26.933601"
        expected = datetime.datetime(year=2019, month=4, day=1, hour=14, minute=10, second=26, microsecond=933601)
        actual = get_datetime(input_time)
        self.assertEqual(expected, actual)
