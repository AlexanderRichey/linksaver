from pymongo import MongoClient


client = MongoClient("mongo", 27017)
db = client.test_database
