import unittest

from util import util
from models.user import User
from models.target import Target


class TestUtils(unittest.TestCase):
    def test_parsing_mongo_to_jsonable_works_with_user(self):
        user = User('name', 'email', 'phone', 'username', 'password')
        parsed = util.parse_mongo_to_jsonable(user.to_json())
        assert parsed == {
            'name': 'name', 'email': 'email', 'id': 'None', 'phone': 'phone',
            'username': 'username', 'password': 'password', 'admin': None
        }

    def test_parsing_mongo_to_jsonable_works_with_target(self):
        target = Target(
            'target_id',
            'name',
            'town',
            'type',
            'x_coordinate',
            'y_coordinate',
            'location_method',
            'location_accuracy',
            'url',
            'created_at',
            True,
            'source',
            True
        )
        parsed = util.parse_mongo_to_jsonable(target.to_json())
        assert parsed == {
            'type': 'Feature',
            'properties': {
                'id': 'target_id',
                'name': 'name',
                'town': 'town',
                'type': 'type',
                'location_method': 'location_method',
                'location_accuracy': 'location_accuracy',
                'url': 'url',
                'created_at': 'created_at',
                'is_ancient': True,
                'source': 'source',
                'is_pending': True
            },
            'geometry': {
                'type': 'Point',
                'coordinates': ['x_coordinate', 'y_coordinate']
            }

        }

    def test_parsing_byte_string_to_dict_works_correctly(self):
        byte_string = b'{"test": "success"}'
        parsed = util.parse_byte_string_to_dict(byte_string)
        self.assertDictEqual(parsed, {'test': 'success'})

    def test_parsing_byte_string_to_dict_works_with_javascript_booleans(self):
        byte_string = b'{"test": true, "works": false}'
        parsed = util.parse_byte_string_to_dict(byte_string)
        self.assertDictEqual(parsed, {'test': True, 'works': False})

    def test_parsing_mongo_to_jsonable_fixes_the_id_key(self):
        test_item = {'_id': 123}
        parsed_item = util.parse_mongo_to_jsonable(test_item)
        self.assertDictEqual(parsed_item, {'id': '123'})
