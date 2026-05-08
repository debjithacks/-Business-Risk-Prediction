import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


load_dotenv()
MONGO_DETAILS = os.getenv("MONGODB_URI")
if not MONGO_DETAILS:
	raise RuntimeError(
		"Missing MongoDB URI. Set MONGODB_URI in your environment (or .env)."
	)

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.business_risk_db

# Collections
user_collection = database.get_collection("users")
risk_data_collection = database.get_collection("risk_history")
chat_collection = database.get_collection("chat_history")