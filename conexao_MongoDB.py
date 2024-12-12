from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["biblioteca_logs"]
user_logs = mongo_db["user_logs"]
