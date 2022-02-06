import unittest
from fetch_from_museovirasto import *
from shapely.geometry import Point
from types import SimpleNamespace


class TestFetchFromMuseovirasto(unittest.TestCase):
    def test_z_to_point(self):
        point = {
            "x": 1,
            "y": 1
        }
        self.assertEqual(z_to_point(SimpleNamespace(**point)), Point(1, 1))

    def test_z_to_point_negative_values(self):
        point = {
            "x": -1,
            "y": 1
        }
        self.assertEqual(z_to_point(SimpleNamespace(**point)), Point(-1, 1))

    def test_date_is_not_filled_when_found(self):
        self.assertEqual(filldate({"created_at": 1}), 1)

    def test_date_is_filled_when_not_present(self):
        row = {
            "created_at": 'None',
            "luontipvm": "1.1.2000"
        }
        self.assertEqual(filldate(row), "2000-01-01")
