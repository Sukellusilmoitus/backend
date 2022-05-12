import datetime
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models.dive import Dive
from models.targetnote import Targetnote
from util.config import SENDER_EMAIL, RECEIVER_EMAIL
from util.mongo import connect_to_db
from util.email_sender import sender

connect_to_db()


class Emailer:
    def __init__(
        self,
        days,
        send_service,
        dive_model,
        targetnote_model,
        sender_email,
        receiver_email
    ):
        """Emailer to send new targets and dives

        Args:
            days (int): how many days old data is sent
        """
        self.dive_model = dive_model
        self.targetnote_model = targetnote_model
        self.dives = []
        self.targetnotes = []
        self.days = days
        self.send_service = send_service
        self.sender_email = sender_email
        self.receiver_email = receiver_email

    def get_dives(self):
        date = datetime.datetime.now() - datetime.timedelta(days=self.days)
        date = date.replace(hour=23, minute=59, second=59)
        self.dives = self.dive_model.objects.raw(
            {'created_at': {'$gte': date}})

    def get_targets(self):
        date = datetime.datetime.now() - datetime.timedelta(days=self.days)
        date = date.replace(hour=23, minute=59, second=59)
        self.targetnotes = self.targetnote_model.objects.raw(
            {'created_at': {'$gte': date}})

    def message_builder(self):
        self.get_dives()
        self.get_targets()

        message = MIMEMultipart('alternative')
        message['Subject'] = 'Sukellusilmoituksia'
        message['From'] = self.sender_email
        message['To'] = self.receiver_email

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

        email_text = email_text.replace('å', 'a*')
        email_text = email_text.replace('ä', 'a"')
        email_text = email_text.replace('ö', 'o"')

        email_text = email_text.replace('Å', 'A*')
        email_text = email_text.replace('Ä', 'A"')
        email_text = email_text.replace('Ö', 'O"')

        part = MIMEText(email_text, 'plain')
        message.attach(part)

        return message.as_string()

    def send_email(self):
        message = self.message_builder()
        self.send_service(message)


if __name__ == '__main__':
    try:
        DAYS = int(sys.argv[1])
    except IndexError:
        DAYS = 7
    email = Emailer(DAYS, sender, Dive, Targetnote,
                    SENDER_EMAIL, RECEIVER_EMAIL)
    email.send_email()
