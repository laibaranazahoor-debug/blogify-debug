
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "blogify_database")

# Check MongoDB URL
if not MONGODB_URL:
    raise ValueError("MONGODB_URL is missing from .env file")

# Connect to MongoDB
client = MongoClient(
    MONGODB_URL,
    serverSelectionTimeoutMS=5000
)

# Select Database
database = client[DATABASE_NAME]

# MongoDB Collections
users_collection = database["users"]
blogs_collection = database["blogs"]
categories_collection = database["categories"]


# Check Database Connection
def check_database_connection():
    try:
        client.admin.command("ping")
        return True

    except Exception as error:
        print("MongoDB connection error:", error)
        return False
