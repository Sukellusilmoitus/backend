import unittest
from unittest.mock import Mock
from emailer import Emailer


mock_sender = Mock()
mock_dive = Mock()
mock_target = Mock()
mock_dive.objects.raw.return_value = []
mock_target.objects.raw.return_value = []


class TestEmailer(unittest.TestCase):
    def test_emailer_calls_the_sender_service(self):
        emailer = Emailer(7, mock_sender, mock_dive, mock_target)
        emailer.send_email()
        mock_sender.assert_called_once()

    def test_getting_dives_works(self):
        emailer = Emailer(7, mock_sender, mock_dive, mock_target)
        emailer.get_dives()
        self.assertEqual(emailer.dives, [])
