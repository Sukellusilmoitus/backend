from pymodm.connection import connect
from util.config import MONGO_URI

if MONGO_URI != None:
    connect(MONGO_URI, alias='app')
