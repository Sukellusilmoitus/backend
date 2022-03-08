import unittest
import pytest
import requests
import mongo
import datetime
from models.user import User
from models.dive import Dive
from models.target import Target
from models.targetnote import Targetnote

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

    def test_data_endpoint_returns_targets(self):
        response = requests.get(f'{BASE_URL}/data').json()
        self.assertGreater(len(response['features']), 1)
        first_feature = response['features'][0]
        self.assertEqual(first_feature['properties']['id'], 1000040915)
        self.assertEqual(first_feature['type'], 'Feature')

    def test_target_endpoint_get_returs_targets(self):
        response = requests.get(f'{BASE_URL}/targets').json()
        self.assertGreater(len(response['features']), 1)

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

    def test_data_endpoint_returns_pending_targets(self):
        target = Target.create(target_id = '9999999999991',
                            name = 'Testihylky',
                            town = 'SaimaaTesti',
                            type = 'Hylky',
                            x_coordinate = 25.0,
                            y_coordinate = 61.0,
                            location_method = 'gpstesti',
                            location_accuracy = 'huonotesti',
                            url = 'https://testiurl.com',
                            created_at = datetime.datetime.now(),
                            is_ancient = False,
                            source = 'ilmoitus',
                            is_pending = True)
        user = User.create(name='test user', email='test@example.com', phone='1234567')
        targetnote = Targetnote(diver=user, target=target)
        targetnote.save()
        response = requests.get(f'{BASE_URL}/targets/pending').json()
        first_feature = response['features'][0]
        self.assertGreater(len(response['features']), 0)
        self.assertTrue(first_feature['target']['properties']['is_pending'])
