from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from textblob import TextBlob
from database import user_collection
from chatbot_routes import router as chatbot_router
from fastapi.staticfiles import StaticFiles
import bcrypt

# Utility function to hash passwords
def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Import the updated async functions
from prediction import (
    store_user_month_data,
    cumulative_prediction,
    generate_risk_history
)
from graph import generate_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserAuth(BaseModel):
    username: str
    password: str
    business_type: Optional[str] = None

# --- RISK ANALYSIS ROUTE ---
@app.post("/upload")
async def upload_data(data: dict):
    user_id = data["user_id"]
    month = data["month"]
    month_data = data["features"]

    # NLP Sentiment Logic
    feedback_text = month_data.get("Feedback", "")
    if feedback_text.strip():
        analysis = TextBlob(feedback_text)
        sentiment_score = (analysis.sentiment.polarity + 1) / 2
        month_data["Sentiment_Score"] = round(sentiment_score, 2)
    else:
        month_data["Sentiment_Score"] = 0.5
    
    raw_feedback = feedback_text
    if "Feedback" in month_data:
        del month_data["Feedback"]

    # Await the database and prediction operations
    await store_user_month_data(user_id, month, month_data)
    result = await cumulative_prediction(user_id)

    return result

# --- GRAPH ROUTE (FIXED) ---
@app.get("/risk-graph/{user_id}")
async def risk_graph(user_id: str):
    data = await generate_risk_history(user_id)
    return generate_graph(data)

# --- AUTHENTICATION ROUTES ---
@app.post("/register")
async def register(user: UserAuth):
    existing_user = await user_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username exists")
    
    hashed_password = hash_password(user.password)

    user_dict = {
        "username": user.username,
        "password": hashed_password,
        "business_type": user.business_type
    }

    await user_collection.insert_one(user_dict)
    return {"message": "Success", "business_type": user.business_type}

def verify_password(input_password: str, stored_password: str):
    return bcrypt.checkpw(
        input_password.encode(),
        stored_password.encode()
    )

@app.post("/login")
async def login(user: UserAuth):
    db_user = await user_collection.find_one({"username": user.username})

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "username": db_user["username"],
        "business_type": db_user.get("business_type", "General Business")
    }
app.include_router(chatbot_router)



app.mount(
    "/audio",
    StaticFiles(directory="bengali_audio_cache"),
    name="audio"
)