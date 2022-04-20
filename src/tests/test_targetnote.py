import unittest
import datetime
from pymodm import errors
from models.targetnote import Targetnote
from models.target import Target
from models.user import User


class TestTargetnote(unittest.TestCase):
    def setUp(self):
        targetnotes = Targetnote.objects.all()
        for targetnote in targetnotes:
            targetnote.delete()

    def test_targetnote_cannot_be_created_without_diver(self):
        target = Target.create(target_id='999999999999',
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
        targetnote = Targetnote(target=target)
        with self.assertRaises(errors.ValidationError):
            targetnote.save()

    def test_targetnote_cannot_be_created_without_target(self):
        user = User.create(
            name='test user', email='test@example.com', phone='2123213223',
            username='username', password='password')
        targetnote = Targetnote(diver=user)
        with self.assertRaises(errors.ValidationError):
            targetnote.save()

    def test_targetnote_can_be_created_with_target_and_diver(self):
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
        user = User.create(
            name='test user', email='test@example.com', phone='1234567',
            username='username', password='password')
        targetnote = Targetnote(diver=user, target=target)
        targetnote.save()
        self.assertIsNotNone(targetnote._id)

    def test_targetnote_is_deleted_when_target_is_deleted(self):
        target = Target.create(target_id='999999999999222',
                               name='Testihylky22',
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
        user = User.create(name='test user 2',
                           email='test@example.com',
                           phone='1234567',
                           username='username2',
                           password='password')
        targetnote = Targetnote.create(diver=user, target=target, miscellaneous='testnote')
        tn_id = targetnote._id
        self.assertIsNotNone(Targetnote.objects.raw({'_id': tn_id}).first())
        target.delete()
        with self.assertRaises(errors.DoesNotExist):
            Targetnote.objects.raw({'_id': tn_id}).first()
        with self.assertRaises(errors.DoesNotExist):
            Target.objects.raw({'_id': '999999999999222'}).first()

    def test_target_is_not_deleted_when_targetnote_is_deleted(self):
        target = Target.create(target_id='9999999999992223',
                               name='Testihylky223',
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
        user = User.create(name='test user 3',
                           email='test@example.com',
                           phone='1234567',
                           username='username3',
                           password='password')
        targetnote = Targetnote.create(diver=user, target=target, miscellaneous='testnote')
        tn_id = targetnote._id
        self.assertIsNotNone(Targetnote.objects.raw({'_id': tn_id}).first())
        targetnote.delete()
        with self.assertRaises(errors.DoesNotExist):
            Targetnote.objects.raw({'_id': tn_id}).first()
        self.assertIsNotNone(Target.objects.raw({'_id': '9999999999992223'}).first())
