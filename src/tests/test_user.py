import unittest
from pymodm import errors
from models.user import User


class TestUser(unittest.TestCase):
    def setUp(self):
        users = User.objects.all()
        for user in users:
            user.delete()

    def test_user_cannot_be_created_without_email_or_phone(self):
        user = User(name='test user')
        with self.assertRaises(errors.ValidationError):
            user.save()

    def test_user_cannot_be_created_without_name(self):
        user = User(phone='1234567', email='test@example.com')
        with self.assertRaises(errors.ValidationError):
            user.save()

    def test_user_can_be_created_with_name_and_email(self):
        user = User(name='test user', email='test@example.com')
        user.save()
        self.assertIsNotNone(user._id)

    def test_user_can_be_created_with_name_and_phone(self):
        user = User(name='test user', phone='1234567')
        user.save()
        self.assertIsNotNone(user._id)

    def test_user_can_be_created_with_name_and_email_and_phone(self):
        user = User(name='test user', email='test@example.com', phone='1234567')
        user.save()
        self.assertIsNotNone(user._id)

    def test_to_json_method_returns_data_in_correct_form(self):
        user = User(name='test user', email='test@example.com')
        json = user.to_json()
        correct_output = {
            'id': 'None',
            'name': 'test user',
            'email': 'test@example.com',
            'phone': None,
            'username': None,
            'password': None,
        }
        self.assertDictEqual(json, correct_output)
