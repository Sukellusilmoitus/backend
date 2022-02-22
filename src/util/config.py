import os
from dotenv import load_dotenv

load_dotenv()

if os.getenv('TEST'):
    MONGO_URI = os.getenv('TEST_MONGO_URI')
else:
    MONGO_URI = os.getenv('MONGO_URI')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_EMAIL_PASSWORD = os.getenv('SENDER_EMAIL_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
SERVER_URL = os.getenv('SERVER_URL')
