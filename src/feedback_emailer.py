from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from util.email_sender import sender
from util.config import SENDER_EMAIL, RECEIVER_EMAIL


class FeedbackEmailer:
    def __init__(self, sender_email, receiver_email):
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.send_service = sender
        self.message = ''

    def build_message(self, feedback, time):
        message = MIMEMultipart('alternative')
        message['Subject'] = 'Palautetta annettu'
        message['From'] = self.sender_email
        message['To'] = self.receiver_email

        email_text = 'Uusi palaute:\n\n'
        email_text += feedback.feedback_text + '\n\n'
        email_text += f'Palaute annettu {time}\n\n'

        email_text += 'Palautteen antoi:\n'
        email_text += f'    Nimi: {feedback.feedback_giver_name}\n'
        email_text += '    Yhteystiedot:\n'
        if feedback.feedback_giver_email:
            email_text += f'        Sähköposti: {feedback.feedback_giver_email}\n'
        if feedback.feedback_giver_phone:
            email_text += f'        Puhelinnumero: {feedback.feedback_giver_phone}\n'

        part = MIMEText(email_text, 'plain')
        message.attach(part)

        self.message = message.as_string()

    def send_email(self, feedback):
        time = datetime.now().strftime('%d.%m.%Y %H:%M')
        self.build_message(feedback, time)
        self.send_service(self.message)


feedback_emailer = FeedbackEmailer(SENDER_EMAIL, RECEIVER_EMAIL)
