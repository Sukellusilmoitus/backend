from pymodm import MongoModel, fields


class Feedback(MongoModel):
    feedback_text = fields.CharField()
    feedback_giver_name = fields.CharField()
    feedback_giver_email = fields.EmailField()
    feedback_giver_phone = fields.CharField()

    class Meta:
        connection_alias = 'app'
        final = True

    @staticmethod
    def create(feedback_text, name, email, phone):
        feedback = Feedback(feedback_text, name, email, phone)
        feedback.save()
        return feedback

    def to_json(self):
        return {
            'id': str(self._id) or None,
            'feedback_text': self.feedback_text,
            'feedback_giver_name': self.feedback_giver_name,
            'feedback_giver_email': self.feedback_giver_email,
            'feedback_giver_phone': self.feedback_giver_phone
        }
