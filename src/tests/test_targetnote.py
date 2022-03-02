import unittest
import datetime
from pymodm import errors
from models.targetnote import Targetnote
from models.target import Target
from models.user import User


class TestTargetnote(unittest.TestCase):
    def setUp(self):
        users = Targetnote.objects.all()
        for user in users:
            user.delete()

    def test_targetnote_cannot_be_created_without_diver(self):
        target = Target.create(target_id = '999999999999',
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
                            source = 'ilmoitus')
        targetnote = Targetnote(target=target)
        with self.assertRaises(errors.ValidationError):
            targetnote.save()

    def test_targetnote_cannot_be_created_without_target(self):
        user = User.create(name='test user', email='test@example.com', phone='2123213223')
        targetnote = Targetnote(diver=user)
        with self.assertRaises(errors.ValidationError):
            targetnote.save()

    def test_targetnote_can_be_created_with_target_and_diver(self):
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
                            source = 'ilmoitus')
        user = User.create(name='test user', email='test@example.com', phone='1234567')
        targetnote = Targetnote(diver=user, target=target)
        targetnote.save()
        self.assertIsNotNone(targetnote._id)
