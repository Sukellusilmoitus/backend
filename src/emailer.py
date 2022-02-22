import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from util.config import SENDER_EMAIL, SENDER_EMAIL_PASSWORD, RECEIVER_EMAIL, SERVER_URL

class Emailer:
    def __init__(self,dive_model, user_model, util, target_model, days):
        self.dive_model = dive_model
        self.user_model = user_model
        self.util = util
        self.target_model = target_model
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

        html = f"""
        <html>
            <body>
                <p>Uudet hylyt ({length_target})</p>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Nimi</th>
                    </tr>"""

        for target in self.targets:
            id = target.to_json()['properties']['id']
            html += f"""
                    <tr>
                        <th><a href='{SERVER_URL}/hylyt/{id}'>{id}</a></th>
                        <th>{target.name}</th>
                    </tr>"""

        html += f"""
                </table>
                <p>Uudet sukellusilmoitukset ({length_dives})</p>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Sukeltaja</th>
                    </tr>"""

        for dive in self.dives:
            id = dive.to_json()['id']
            html += f"""
                    <tr>
                        <th>{id}</th>
                        <th>{dive.diver.name}</th>
                    </tr>"""

        html += """
                </table>
            </body>
        </html>"""

        part = MIMEText(html, 'html')
        message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
