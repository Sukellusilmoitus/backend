from flask import request
from flask_restx import Namespace, Resource
from models.feedback import Feedback
from util import util
from feedback_emailer import feedback_emailer

api = Namespace('feedback')


@api.route('/')
class FeedbackApi(Resource):
    def get(self):
        feedback = Feedback.objects.all()
        data = [fb.to_json() for fb in feedback]
        return {'data': data}

    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        feedback_text = data['feedback_text']
        feedback_giver_name = data['feedback_giver_name']
        feedback_giver_email = data['feedback_giver_email']
        feedback_giver_phone = data['feedback_giver_phone']
        created_feedback = Feedback.create(
            feedback_text, feedback_giver_name, feedback_giver_email, feedback_giver_phone)

        feedback_emailer.send_email(created_feedback)

        return {'data': {'feedback': created_feedback.to_json()}}, 201
