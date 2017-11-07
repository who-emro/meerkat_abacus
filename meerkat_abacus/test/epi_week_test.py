import unittest

from datetime import datetime

from meerkat_abacus.util import epi_year_start_date


class EpiWeekTest(unittest.TestCase):
    def test_epi_year_start_for_international_config(self):
        expected_epi_year_start_date = datetime(2015, 1, 1)
        date = datetime(2015, 5, 25)
        self.assertEqual(expected_epi_year_start_date, epi_year_start_date(date, "international"))

    def test_epi_year_start_for_custom_weekday(self):
        year = 2016
        first_weekdays_in_year_days = [4, 5, 6, 7, 1, 2, 3]
        first_weekdays_in_year_datetimes = [datetime(year, 1, day) for day in first_weekdays_in_year_days]
        date = datetime(2016, 6, 14)

        for weekday, expected_epi_year_start_datetime in enumerate(first_weekdays_in_year_datetimes):
            epi_config = "day:{!r}".format(weekday)
            actual_epi_year_start_datetime = epi_year_start_date(date, epi_config)
            self.assertEqual(expected_epi_year_start_datetime, actual_epi_year_start_datetime)

    def test_epi_year_start_for_custom_start_date(self):
        epi_config = {
            2016: datetime(2016, 1, 2),
            2017: datetime(2016, 12, 30)
        }
        test_data = [
            {"date": datetime(2016, 3, 5), "expected_year": 2016},
            {"date": datetime(2016, 12, 31), "expected_year": 2017},
            {"date": datetime(2017, 4, 24), "expected_year": 2017}
        ]
        for _test in test_data:
            expected_datetime = epi_config[_test["expected_year"]]
            actual_datetime = epi_year_start_date(_test["date"], epi_config)
            self.assertEqual(expected_datetime, actual_datetime)
