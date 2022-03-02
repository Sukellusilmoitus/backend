# pylint: disable=unused-import
import datetime
import smtplib
import ssl
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from util.config import SENDER_EMAIL, SENDER_EMAIL_PASSWORD, RECEIVER_EMAIL
from models.dive import Dive
from models.targetnote import Targetnote
from models.user import User
import mongo



class Emailer:
    def __init__(self,days):
        """Emailer to send new targets and dives

        Args:
            days (int): how many days old data is sent
        """
        self.dive_model = Dive
        self.user_model = User
        self.targetnote_model = Targetnote
        self.dives = []
        self.targetnotes = []
        self.days = days

    def get_dives(self):
        date = datetime.datetime.now() - datetime.timedelta(days=self.days)
        date = date.replace(hour=23, minute=59, second=59)
        self.dives = self.dive_model.objects.raw({'created_at': {'$gte': date}})

    def get_targets(self):
        date = datetime.datetime.now() - datetime.timedelta(days=self.days)
        date = date.replace(hour=23, minute=59, second=59)
        self.targetnotes = self.targetnote_model.objects.raw({'created_at': {'$gte': date}})

    def send_email(self):
        self.get_dives()
        self.get_targets()
        sender_email = SENDER_EMAIL
        receiver_email = RECEIVER_EMAIL
        password = SENDER_EMAIL_PASSWORD

        message = MIMEMultipart('alternative')
        message['Subject'] = 'Sukellusilmoituksia'
        message['From'] = sender_email
        message['To'] = receiver_email

        length_target = len(list(self.targetnotes))
        length_dives = len(list(self.dives))

        email_text = ''
        email_text += f'Uudet hylkyilmoitukset ({length_target}):\n'

        for targetnote in self.targetnotes:
            target_json = targetnote.to_json()
            email_text += f"""
            Hylyn nimi: {target_json['target']['properties']['name']}
            Alue: {target_json['target']['properties']['town']}
            Tyyppi: {target_json['target']['properties']['type']}
            Koodrinaatit: {target_json['target']['geometry']['coordinates']}
            Määrittelytapa: {target_json['target']['properties']['location_method']}
            Tarkkuus: {target_json['target']['properties']['location_accuracy']}
            Ilmoittaja: {target_json['diver']['name']}
            Puh: {target_json['diver']['phone']}
            Email: {target_json['diver']['email']}
            Lisäinfoa: {target_json['miscellaneous']}
            """

        email_text += f'\n\nUudet sukellusilmoitukset ({length_dives}):\n'

        for dive in self.dives:
            dive_json = dive.to_json()
            email_text += f"""
            Sukeltaja: {dive_json['diver']['name']}
            Kohde: {dive_json['target']['properties']['name']}"""
            if dive_json['location_correct'] is True:
                email_text += """
            Oliko koodrinaatit oikein: Kyllä"""
            else:
                email_text += f"""
            Oliko koordinaatit oikein: Ei
            Uudet koordinaatit: {dive_json['new_x_coordinate']}, {dive_json['new_y_coordinate']}
            Uusien koordinaattien selite: {dive_json['new_location_explanation']}"""
            if dive_json['change_text'] == '':
                email_text += """
            Hylyssä havaittu muutoksia: Ei"""
            else:
                email_text += f"""
            Hylyssä havaittu muutoksia: Kyllä
            Muutokset: {dive_json['change_text']}"""
            email_text += f"""
            Lisäinfo: {dive_json['miscellanious']}
            """

        email_text = email_text.replace('å','a*')
        email_text = email_text.replace('ä','a"')
        email_text = email_text.replace('ö','o"')

        email_text = email_text.replace('Å','A*')
        email_text = email_text.replace('Ä','A"')
        email_text = email_text.replace('Ö','O"')

        print(email_text)

        part = MIMEText(email_text, 'plain')
        message.attach(part)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )

if __name__ == '__main__':
    try:
        DAYS = int(sys.argv[1])
    except IndexError:
        DAYS = 7
    email = Emailer(DAYS)
    email.send_email()
