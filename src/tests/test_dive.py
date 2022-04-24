import unittest
import datetime
from pymodm import errors
from models.dive import Dive
from models.target import Target
from models.user import User

class TestDive(unittest.TestCase):
    def setUp(self):
        dives = Dive.objects.all()
        for dive in dives:
            dive.delete()

    def test_target_is_not_deleted_when_dive_is_deleted(self):
        target1 = Target.create(target_id='99999999999910',
                               name='Testihylky0',
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

        user1 = User.create(name='test user11',
                           email='test1@example.com',
                           phone='1234567',
                           password='test',
                           username='test11'
                           )

        dive = Dive.create(diver=user1,
                           target=target1,
                           location_correct=True,
                           created_at=datetime.datetime.now(),
                           new_x_coordinate=None,
                           new_y_coordinate=None,
                           new_location_explanation=None,
                           change_text='testimuutoksia',
                           miscellaneous=None,
                           divedate=datetime.datetime.now())

        dive_id = dive._id
        self.assertIsNotNone(Dive.objects.raw({'_id': dive_id}).first())
        dive.delete()
        with self.assertRaises(Exception):
            Dive.objects.raw({'_id': dive_id}).first()
        self.assertIsNotNone(Target.objects.raw({'_id': '99999999999910'}).first())

    def test_dive_is_deleted_when_target_is_deleted(self):
        target1 = Target.create(target_id='99999999999911',
                               name='Testihylky01',
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

        user1 = User.create(name='test user11',
                           email='test1@example.com',
                           phone='1234567',
                           password='test',
                           username='test11'
                           )

        dive = Dive.create(diver=user1,
                           target=target1,
                           location_correct=True,
                           created_at=datetime.datetime.now(),
                           new_x_coordinate=None,
                           new_y_coordinate=None,
                           new_location_explanation=None,
                           change_text='testimuutoksia',
                           miscellaneous=None,
                           divedate=datetime.datetime.now())

        dive_id = dive._id
        self.assertIsNotNone(Dive.objects.raw({'_id': dive_id}).first())
        target1.delete()
        with self.assertRaises(errors.DoesNotExist):
            Dive.objects.raw({'_id': dive_id}).first()
        with self.assertRaises(errors.DoesNotExist):
            Target.objects.raw({'_id': '99999999999911'}).first()
