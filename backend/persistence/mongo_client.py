# backend/persistence/mongo_client.py
from pymongo import MongoClient
from .. import config

_client = None

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(config.MONGO_URI)
    return _client

def get_db():
    return get_client()["crop_price_db"]

def get_users_collection():
    return get_db()["users"]

def get_predictions_collection():
    return get_db()["predictions"]
