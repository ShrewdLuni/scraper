import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv('DATABASE_URL')

client = MongoClient(uri, server_api=ServerApi('1'))

db = client["ScraperDB"]
products_collection = client["ScraperDB"].Products
opinions_collection = client["ScraperDB"].Opinions