import smtplib
from util.config import SENDER_EMAIL, SENDER_EMAIL_PASSWORD, RECEIVER_EMAIL


def sender(message):
    sender_email = SENDER_EMAIL
    receiver_email = RECEIVER_EMAIL
    password = SENDER_EMAIL_PASSWORD
    with smtplib.SMTP('smtp.office365.com', 587) as server:
        server.ehlo()
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message
        )
        server.close()
