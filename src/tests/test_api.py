# pylint: disable=unused-import,line-too-long
import unittest
import datetime
import pytest
import requests
import mongo
from models.user import User
from models.dive import Dive
from models.target import Target
from models.targetnote import Targetnote

BASE_URL = 'http://localhost:5000/api'


@pytest.mark.api
class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        print('setupRUNN')
        users = User.objects.all()
        dives = Dive.objects.all()
        targets = Target.objects.raw({
            '$or':
                [{'source': {'$eq': 'ilmoitus'}},
                {'name': {'$eq': 'overlapHylky'}}]
        }).all()
        for user in users:
            user.delete()
        for dive in dives:
            dive.delete()
        for target in targets:
            target.delete()

    def test_api_is_up(self):
        response = requests.get(f'{BASE_URL}/healthcheck').json()
        self.assertEqual(response['status'], 'ok')

    def test_data_endpoint_returns_targets(self):
        response = requests.get(f'{BASE_URL}/data').json()
        self.assertGreater(len(response['features']), 1500)
        first_feature = response['features'][0]
        self.assertEqual(first_feature['geometry']['type'], 'Point')
        self.assertEqual(first_feature['type'], 'Feature')

    def test_target_endpoint_get_returs_targets(self):
        response = requests.get(f'{BASE_URL}/targets').json()
        self.assertGreater(len(response['features']), 1500)

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
        target = Target.create(target_id='9999999999991',
                               name='Testihylky',
                               town='SaimaaTesti',
                               type='Hylky',
                               x_coordinate=25.0,
                               y_coordinate=61.0,
                               location_method='gpstesti',
                               location_accuracy='huonotesti',
                               url='https://testiurl.com',
                               created_at=datetime.datetime.now(),
                               is_ancient=False,
                               source='ilmoitus',
                               is_pending=True)
        user = User.create(name='test user', email='test@example.com', phone='1234567')
        targetnote = Targetnote(diver=user, target=target)
        targetnote.save()
        response = requests.get(f'{BASE_URL}/admin/pending?_end=10&_order=ASC&_sort=id&_start=0').json()
        first_feature = response[0]
        self.assertGreater(len(response), 0)
        self.assertTrue(first_feature['is_pending'])

    def test_admin_endpoint_returns_overlapping_targets(self):
        self.setUp()
        Target.create(target_id='99999992',
                      name='overlapHylky',
                      town='SaimaaTesti',
                      type='Hylky',
                      x_coordinate=25.223335,
                      y_coordinate=61.545545,
                      location_method='gpstesti',
                      location_accuracy='huonotesti',
                      url='https://testiurl.com',
                      created_at=datetime.datetime.now(),
                      is_ancient=False,
                      source='museovirasto',
                      is_pending=False)
        Target.create(target_id='9999991',
                      name='overlapHylky',
                      town='SaimaaTesti',
                      type='Hylky',
                      x_coordinate=25.223335,
                      y_coordinate=61.545545,
                      location_method='gpstesti',
                      location_accuracy='huonotesti',
                      url='https://testiurl.com',
                      created_at=datetime.datetime.now(),
                      is_ancient=False,
                      source='ilmoitus',
                      is_pending=True)
        response = requests.get(f'{BASE_URL}/admin/duplicates?_end=10&_order=ASC&_sort=id&_start=0').json()
        self.assertGreater(len(response), 0)
        self.assertIn(response[0]['id'], ['9999991', '99999992'])
        self.assertIn(response[1]['id'], ['9999991', '99999992'])

    def test_admin_endpoint_returns_overlapping_targets_by_4dec_precicion(self):
        self.setUp()
        Target.create(target_id='99999994',
                      name='overlapHylky',
                      town='SaimaaTesti',
                      type='Hylky',
                      x_coordinate=25.223335,
                      y_coordinate=61.545545,
                      location_method='gpstesti',
                      location_accuracy='huonotesti',
                      url='https://testiurl.com',
                      created_at=datetime.datetime.now(),
                      is_ancient=False,
                      source='museovirasto',
                      is_pending=False)
        Target.create(target_id='9999995',
                      name='overlapHylky',
                      town='SaimaaTesti',
                      type='Hylky',
                      x_coordinate=25.223322,
                      y_coordinate=61.5455,
                      location_method='gpstesti',
                      location_accuracy='huonotesti',
                      url='https://testiurl.com',
                      created_at=datetime.datetime.now(),
                      is_ancient=False,
                      source='ilmoitus',
                      is_pending=False)
        response = requests.get(f'{BASE_URL}/admin/duplicates?_end=10&_order=ASC&_sort=id&_start=0').json()
        self.assertGreater(len(response), 0)
        self.assertIn(response[0]['id'], ['9999995', '99999994'])
        self.assertIn(response[1]['id'], ['9999995', '99999994'])
