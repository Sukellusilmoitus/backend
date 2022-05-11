from pymodm.connection import connect
from util.config import MONGO_URI


def connect_to_db():
    connect(MONGO_URI, alias='app')
