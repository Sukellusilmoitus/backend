import datetime
from mimetypes import MimeTypes
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        self.targets = self.target_model.objects.raw({'source': 'ilmoitus', 'created_at': {'$gte': date}})

