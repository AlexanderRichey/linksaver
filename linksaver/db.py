import os
from pymongo import MongoClient, TEXT

DB_CONNECTION = os.getenv("DB_CONNECTION")

client = MongoClient(DB_CONNECTION)
db = client.test

db.users.create_index("email", unique=True)
db.items.create_index("email")
db.items.create_index([("title", TEXT,), ("body", TEXT,)])
