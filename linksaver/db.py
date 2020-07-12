import os
from pymongo import MongoClient

DB_CONNECTION = os.getenv("DB_CONNECTION")

client = MongoClient(DB_CONNECTION)
db = client.test
