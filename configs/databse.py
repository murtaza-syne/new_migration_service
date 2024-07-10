from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv

import os
load_dotenv()

username = os.getenv("mongo_username")
password = os.getenv("mongo_password")


encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

uri = f"mongodb+srv://{encoded_username}:{encoded_password}@atlascluster.gzcnpzn.mongodb.net/?retryWrites=true&w=majority&appName=AtlasCluster"

client = MongoClient(uri)


try:
    client.admin.command('ping')
    db = client.test_db
    collection_name = db["test_collection"]
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Connection failed: {e}")