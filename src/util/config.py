import os
from dotenv import load_dotenv

load_dotenv()

if os.getenv('TEST'):
    MONGO_URI = os.getenv('TEST_MONGO_URI')
else:
    MONGO_URI = os.getenv('MONGO_URI')
