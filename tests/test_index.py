import unittest
import json
import src.mongo as Mongo

from unittest.mock import patch
from src.index import app, Dive, User, Target

test_data = {
    'email': 'test@test.com',
    'target_id': 1000041015,
    'location_correct': True
}

test_target = {
    "name": "('test test',)",
    "town": "('Imatra',)",
    "type": "('alusten hylyt,  ,  ,',)",
    "x_coordinate": "('28.782011',)",
    "y_coordinate": "('61.226582',)",
    "location_method": "(None,)",
    "location_accuracy": "(None,)",
    "url": "https://www.kyppi.fi/to.aspx?id=112.1000041015",
    "created_at": "2021-05-06",
    "id": "1000041015"
}

class TestTests(unittest.TestCase):
    def test_api_is_running(self):
        res = send_get('api/helloworld')
        assert res.status_code == 200
        assert b'Hello, World!' in res.data
    
    def test_api_healthcheck(self):
        res = send_get('api/healthcheck')
        assert res.status_code == 200
        assert b'ok' in res.data

    def test_api_returns_wreck_data(self):
        res = send_get('api/data')
        assert res.status_code == 200
        assert len(res.data) != 0
    
    # def test_test_user_exists(self):
    #     res = send_get('api/users')
    #     assert res.status_code == 200
    #     assert b'test@test.com' in res.data

    def test_add_user(self):
        res = send_post('/api/users', {'name': "test name", 'email': "email@email.com", 'phone': "0000000000"})
        assert res.status_code == 201

    # def test_dives_can_be_updated(self):
    #     res = post_dive('api/dives', test_data)
    #     assert res.status_code == 200
    #     assert b'test@test.com' in res.data
    #     assert b'1000041015' in res.data

    # def test_api_returns_dives(self):
    #     res = send_get('api/dives')
    #     assert res.status_code == 200
    #     assert len(res.data) != 0

    # def test_api_returns_targets(self):
    #     res = send_get('api/targets')
    #     assert res.status_code == 200
    #     assert len(res.data) != 0
    
    def test_targets_can_be_added(self):
        res = send_post('api/targets', test_target)
        assert res.status_code == 201
        assert b'test test' in res.data

def fake_user(name, email, phone):
    return User(name, email, phone)

def fake_dive(diver, target, location_correct, created_at):
    return None

def fake_target(
        target_id,
        name,
        town,
        type,
        x_coordinate,
        y_coordinate,
        location_method,
        location_accuracy,
        url,
        created_at
    ):
    return Target(
            target_id=target_id,
            name=name,
            town=town,
            type=type,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            location_method=location_method,
            location_accuracy=location_accuracy,
            url=url,
            created_at=created_at
        )

@patch.object(User.objects, 'values', None)
@patch.object(Target.objects, 'values', None)
@patch.object(Dive.objects, 'values', None)
def send_get(url):
    res = app.test_client().get(url)
    return res

@patch.object(User, 'create', fake_user)
@patch.object(Target, 'create', fake_target)
@patch.object(Dive, 'create', fake_dive)
def send_post(url, data):
    res = app.test_client().post(url, data=data)
    return res

