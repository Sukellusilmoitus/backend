import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from util.config import SENDER_EMAIL, SENDER_EMAIL_PASSWORD, RECEIVER_EMAIL
from models.dive import Dive
from models.target import Target
from models.user import User
from util import util
import mongo


class Emailer:
    def __init__(self,days):
        """Emailer to send new targets and dives

        Args:
            dive_model (pymodm.base.models.TopLevelMongoModelMetaclass): dive mongo model
            user_model (pymodm.base.models.TopLevelMongoModelMetaclass): user mongo model
            util (module): util
            target_model (pymodm.base.models.TopLevelMongoModelMetaclass): target mongo model
            days (int): how many days old data is sent
        """
        self.dive_model = Dive
        self.user_model = User
        self.util = util
        self.target_model = Target
        self.dives = []
        self.targets = []
        self.days = days

    def get_dives(self):
        date = datetime.datetime.now() - datetime.timedelta(days=self.days)
        date = date.replace(hour=23, minute=59, second=59)
        self.dives = self.dive_model.objects.raw({'created_at': {'$gte': date}})

    def get_targets(self):
        date = datetime.datetime.now() - datetime.timedelta(days=self.days)
        date = date.replace(hour=23, minute=59, second=59)
        self.targets = self.target_model.objects.raw(
            {'source': 'ilmoitus', 'created_at': {'$gte': date}})

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

        length_target = len(list(self.targets))
        length_dives = len(list(self.dives))

        email_text = ''
        email_text += f'Uudet hylkyilmoitukset ({length_target}):\n'

        for target in self.targets:
            target_json = target.to_json()
            email_text += f"""
            Hylyn nimi: {target_json['properties']['name']}
            Alue: {target_json['properties']['town']}
            Tyyppi: {target_json['properties']['type']}
            Koodrinaatit: {target_json['geometry']['coordinates']}
            Määrittelytapa: {target_json['properties']['location_method']}
            Tarkkuus: {target_json['properties']['location_accuracy']}
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
            Oliko koodrinaatit oikein: Ei
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

        part = MIMEText(email_text, 'plain')
        message.attach(part)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )

if __name__ == '__main__':
    email = Emailer(7)
    email.send_email()
