import unittest
from pymodm import errors
from models.feedback import Feedback


class TestTarget(unittest.TestCase):
    def setUp(self):
        feedbacks = Feedback.objects.all()
        for fb in feedbacks:
            fb.delete()

    def test_feedback_is_not_submitted_without_email_and_phone(self):
        feedback = Feedback('feeding back', 'tester')
        with self.assertRaises(errors.ValidationError):
            feedback.save()

    def test_feedback_cannot_be_created_without_feedback(self):
        feedback = Feedback(feedback_giver_name='tester',
                            feedback_giver_phone='1234567')
        with self.assertRaises(errors.ValidationError):
            feedback.save()

    def test_feedback_cannot_be_created_without_name(self):
        feedback = Feedback(feedback_text='tester',
                            feedback_giver_phone='1234567')
        with self.assertRaises(errors.ValidationError):
            feedback.save()

    def test_feedback_return_correct_json(self):
        feedback = Feedback(feedback_text='tester',
                            feedback_giver_name='tester',
                            feedback_giver_phone='1234567')
        json = feedback.to_json()
        correct_output = {
            'id': 'None',
            'feedback_text': 'tester',
            'feedback_giver_name': 'tester',
            'feedback_giver_email': None,
            'feedback_giver_phone': '1234567'
        }
        self.assertDictEqual(json, correct_output)
