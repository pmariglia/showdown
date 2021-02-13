import unittest
from unittest import mock
from datetime import date

from data.parse_smogon_stats import get_smogon_stats_file_name


class TestGetSmogonStatsFileName(unittest.TestCase):
    def setUp(self):
        self.datetime_patch = mock.patch('data.parse_smogon_stats.datetime')
        self.addCleanup(self.datetime_patch.stop)
        self.datetime_mock = self.datetime_patch.start()

        self.current_date_mock = date(2019, 6, 5)

    def test_returns_single_digit_month_properly(self):
        self.datetime_mock.now.return_value = self.current_date_mock
        file_name = get_smogon_stats_file_name('gen7ou', month_delta=2)

        self.assertEqual('https://www.smogon.com/stats/2019-04/chaos/gen7ou-0.json', file_name)

    def test_works_with_double_digit_month(self):
        self.current_date_mock = date(2019, 11, 5)
        self.datetime_mock.now.return_value = self.current_date_mock
        file_name = get_smogon_stats_file_name('gen7ou', month_delta=2)

        self.assertEqual('https://www.smogon.com/stats/2019-09/chaos/gen7ou-0.json', file_name)

    def test_returns_previous_year_properly(self):
        self.current_date_mock = date(2019, 1, 5)
        self.datetime_mock.now.return_value = self.current_date_mock
        file_name = get_smogon_stats_file_name('gen7ou', month_delta=2)

        self.assertEqual('https://www.smogon.com/stats/2018-11/chaos/gen7ou-0.json', file_name)
