import smtplib
import ssl
from util.config import SENDER_EMAIL, SENDER_EMAIL_PASSWORD, RECEIVER_EMAIL


def sender(message):
    sender_email = SENDER_EMAIL
    receiver_email = RECEIVER_EMAIL
    password = SENDER_EMAIL_PASSWORD
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message
        )
