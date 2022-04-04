import unittest
from unittest.mock import Mock
import datetime
from models.target import Target
from email_services.weekly_emailer import Emailer


mock_sender = Mock()
mock_dive = Mock()
mock_target = Mock()
mock_dive.objects.raw.return_value = []
mock_target.objects.raw.return_value = []

sender_email = 'sender@email.com'
receiver_email = 'receiver@email.com'


class TestEmailer(unittest.TestCase):
    def test_emailer_calls_the_sender_service(self):
        emailer = Emailer(7, mock_sender, mock_dive,
                          mock_target, sender_email, receiver_email)
        emailer.send_email()
        mock_sender.assert_called_once()

    def test_getting_dives_works(self):
        emailer = Emailer(7, mock_sender, mock_dive,
                          mock_target, sender_email, receiver_email)
        emailer.get_dives()
        self.assertEqual(emailer.dives, [])

    def test_getting_targets_works(self):
        emailer = Emailer(7, mock_sender, mock_dive,
                          mock_target, sender_email, receiver_email)
        emailer.get_targets()
        self.assertEqual(emailer.targetnotes, [])

    def test_message_has_correct_headers(self):
        emailer = Emailer(7, mock_sender, mock_dive,
                          mock_target, sender_email, receiver_email)
        message = emailer.message_builder()
        self.assertNotEqual(message.find('From: sender@email.com'), -1)
        self.assertNotEqual(message.find('To: receiver@email.com'), -1)
        self.assertNotEqual(message.find('Subject: Sukellusilmoituksia'), -1)
        self.assertNotEqual(message.find('MIME-Version: 1.0'), -1)
