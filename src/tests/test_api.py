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
            phone='050-1234567',
            password='test',
            username='test'
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
        user = User.create(name='test user',
                           email='test@example.com',
                           phone='1234567',
                           password='test',
                           username='test'
                           )
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

    def test_after_registering_login_with_correct_credentials_returns_auth(self):
        self.setUp()
        res = requests.post(f'{BASE_URL}/register', json={
            'name': 'name',
            'email': 'email@email.com',
            'username': 'username4321',
            'password': 'password'
        })
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('message', res.json().keys())
        res = requests.post(f'{BASE_URL}/login', json={
            'username': 'username4321',
            'password': 'password'
        })
        self.assertEqual(res.status_code, 200)
        token = res.json()['auth']
        self.assertTrue(len(token) > 0)

    def test_token_required_route_requires_auth_token(self):
        self.setUp()
        requests.post(f'{BASE_URL}/register', json={
            'name': 'name',
            'email': 'email@email.com',
            'username': 'username4321',
            'password': 'password'
        })
        res = requests.post(f'{BASE_URL}/login', json={
            'username': 'username4321',
            'password': 'password'
        })
        token = res.json()['auth']
        res = requests.get(f'{BASE_URL}/test')
        self.assertEqual(res.status_code, 401)
        res = requests.get(f'{BASE_URL}/test', headers={
            'X-ACCESS-TOKEN': token
        })
        self.assertEqual(res.status_code, 200)

    def test_after_correct_registering_login_with_incorrect_credentials_does_not_return_auth(self):
        self.setUp()
        res = requests.post(f'{BASE_URL}/register', json={
            'name': 'name',
            'email': 'email@email.com',
            'username': 'username4321',
            'password': 'password'
        })
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('message', res.json().keys())
        res = requests.post(f'{BASE_URL}/login', json={
            'username': 'username4321',
            'password': 'pasword'
        })
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('auth', res.json().keys())
        self.assertEqual(res.json()['message'], 'Väärä käyttäjätunnus tai salasana')

    def test_register_returns_error_message_if_username_is_taken(self):
        self.setUp()
        res = requests.post(f'{BASE_URL}/register', json={
            'name': 'name',
            'email': 'email@email.com',
            'username': 'username4321',
            'password': 'password'
        })
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('message', res.json().keys())
        res = requests.post(f'{BASE_URL}/register', json={
            'name': 'name',
            'email': 'email@email.com',
            'username': 'username4321',
            'password': 'password'
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['message'], 'username taken')

    def test_user_targetnotes_returns_only_users_targetnotes(self):
        target1 = Target.create(target_id='9999999999991',
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
        target2 = Target.create(target_id='9999999999911',
                               name='Testihylky2',
                               town='SaimaaTesti2',
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
        user1 = User.create(name='test user1',
                           email='test1@example.com',
                           phone='1234567',
                           password='test',
                           username='test1'
                           )
        user2 = User.create(name='test user2',
                           email='test2@example.com',
                           phone='12345677',
                           password='test',
                           username='test2'
                           )
        Targetnote.create(diver=user1, target=target1)
        Targetnote.create(diver=user2, target=target2)
        response = requests.get(f'{BASE_URL}/targets/user/test1').json()
        data = response['data']
        first_feature = data[0]
        self.assertEqual(len(data), 1)
        self.assertTrue(first_feature['target']['properties']['is_pending'])
        self.assertEqual(first_feature['target']['properties']['name'], 'Testihylky')
        self.assertEqual(first_feature['diver']['name'], 'test user1')

    def test_user_targetnotes_returns_empty_data_dict_if_no_targetnotes(self):
        target2 = Target.create(target_id='9999999999911',
                               name='Testihylky2',
                               town='SaimaaTesti2',
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
        User.create(name='test user1',
                    email='test1@example.com',
                    phone='1234567',
                    password='test',
                    username='test1'
                    )
        user2 = User.create(name='test user2',
                           email='test2@example.com',
                           phone='12345677',
                           password='test',
                           username='test2'
                           )
        Targetnote.create(diver=user2, target=target2)
        response = requests.get(f'{BASE_URL}/targets/user/test1').json()
        data = response['data']
        self.assertEqual(len(data), 0)

    def test_user_dives_returns_only_users_dives(self):
        target1 = Target.create(target_id='9999999999991',
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
        target2 = Target.create(target_id='9999999999911',
                               name='Testihylky2',
                               town='SaimaaTesti2',
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
        user1 = User.create(name='test user1',
                           email='test1@example.com',
                           phone='1234567',
                           password='test',
                           username='test1'
                           )
        user2 = User.create(name='test user2',
                           email='test2@example.com',
                           phone='12345677',
                           password='test',
                           username='test2'
                           )
        Dive.create(diver=user1,
                    target=target1,
                    location_correct=True,
                    created_at=datetime.datetime.now(),
                    divedate=datetime.datetime.now(),
                    new_x_coordinate=None,
                    new_y_coordinate=None,
                    new_location_explanation=None,
                    change_text='testimuutoksia',
                    miscellaneous=None,
                    divedate=datetime.datetime.now())
        Dive.create(diver=user1,
                    target=target2,
                    location_correct=True,
                    created_at=datetime.datetime.now(),
                    divedate=datetime.datetime.now(),
                    new_x_coordinate=None,
                    new_y_coordinate=None,
                    new_location_explanation=None,
                    change_text='testimuutoksia2',
                    miscellaneous='terveisiä',
                    divedate=datetime.datetime.now())
        Dive.create(diver=user2,
                    target=target1,
                    location_correct=True,
                    created_at=datetime.datetime.now(),
                    divedate=datetime.datetime.now(),
                    new_x_coordinate=None,
                    new_y_coordinate=None,
                    new_location_explanation=None,
                    change_text='väärä user',
                    miscellaneous='moi',
                    divedate=datetime.datetime.now())
        response = requests.get(f'{BASE_URL}/dives/user/test1').json()
        data = response['data']
        first_feature = data[0]
        self.assertEqual(len(data), 2)
        self.assertIn(first_feature['target']['properties']['name'], ['Testihylky2', 'Testihylky'])
        self.assertEqual(first_feature['diver']['name'], 'test user1')

    def test_user_dives_return_empty_dict_if_no_dives(self):
        target1 = Target.create(target_id='9999999999991',
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
        Target.create(target_id='9999999999911',
                               name='Testihylky2',
                               town='SaimaaTesti2',
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
        User.create(name='test user1',
                           email='test1@example.com',
                           phone='1234567',
                           password='test',
                           username='test1'
                           )
        user2 = User.create(name='test user2',
                           email='test2@example.com',
                           phone='12345677',
                           password='test',
                           username='test2'
                           )
        Dive.create(diver=user2,
                    target=target1,
                    location_correct=True,
                    created_at=datetime.datetime.now(),
                    divedate=datetime.datetime.now(),
                    new_x_coordinate=None,
                    new_y_coordinate=None,
                    new_location_explanation=None,
                    change_text='väärä user',
                    miscellaneous='moi',
                    divedate=datetime.datetime.now())
        response = requests.get(f'{BASE_URL}/dives/user/test1').json()
        data = response['data']
        self.assertEqual(len(data), 0)

    def test_user_dives_return_error_message_if_user_not_found(self):
        response = requests.get(f'{BASE_URL}/dives/user/test1')
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('data', response.json().keys())
        self.assertEqual(response.json()['message'], 'user not found')

    def test_user_targetnotes_return_error_message_if_user_not_found(self):
        response = requests.get(f'{BASE_URL}/targets/user/test1')
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('data', response.json().keys())
        self.assertEqual(response.json()['message'], 'user not found')

    def test_user_data_doesnt_update_without_auth(self):
        response = requests.put(f'{BASE_URL}/updateUser')
        self.assertEqual(response.status_code, 401)

    def test_user_data_returns_updated_token_when_successful(self):
        self.setUp()
        response = requests.post(f'{BASE_URL}/register', json={
            'name': 'name',
            'email': 'email@email.com',
            'username': 'username4321',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        response = requests.post(f'{BASE_URL}/login', json={
            'username': 'username4321',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        token = response.json()['auth']
        response = requests.put(f'{BASE_URL}/updateUser', json={
                'username': 'username4321',
                'name': 'updated name',
                'email': 'updated@email.com',
                'phone': '9876543210'
            }, headers={
                'X-ACCESS-TOKEN': token
            }
        )
        self.assertEqual(response.status_code, 201)
        
