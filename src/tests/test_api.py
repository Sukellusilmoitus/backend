import unittest
import pytest
import requests
import mongo
from models.user import User
from models.dive import Dive

BASE_URL = 'http://localhost:5000/api'


@pytest.mark.api
class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        users = User.objects.all()
        dives = Dive.objects.all()
        for user in users:
            user.delete()
        for dive in dives:
            dive.delete()

    def test_api_is_up(self):
        response = requests.get(f'{BASE_URL}/healthcheck').json()
        self.assertEqual(response['status'], 'ok')

    def test_data_endpoint_returns_wrecks(self):
        response = requests.get(f'{BASE_URL}/data').json()
        self.assertGreater(len(response['features']), 1)
        first_feature = response['features'][0]
        self.assertEqual(first_feature['properties']['id'], 1000037580)
        self.assertEqual(first_feature['type'], 'Feature')

    def test_target_endpoint_get_returs_targets(self):
        response = requests.get(f'{BASE_URL}/targets').json()
        self.assertGreater(len(response['data']), 1)

    def test_user_endpoint_get_returns_users(self):
        user = User.create(
            name='test user',
            email='test@example.com',
            phone='050-1234567'
        )
        response = requests.get(f'{BASE_URL}/users').json()
        self.assertEqual(len(response['data']), 1)
        self.assertEqual(response['data'][0]['name'], user.name)
    
    def test_new_coordinates_targets(self):
        response = requests.get(f'{BASE_URL}/targets/newcoordinates')
        self.assertEqual(response.status_code, 200)
