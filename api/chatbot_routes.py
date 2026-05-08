from fastapi import APIRouter
from pydantic import BaseModel

from chatbot_engine import generate_chat_response
from datetime import datetime
from database import chat_collection
from fastapi.responses import FileResponse
from report_generator import generate_business_report
from prediction import cumulative_prediction
from database import risk_data_collection
from pdf_graphs import generate_risk_profit_graphs
from chat_report_generator import generate_chat_history_report
from translate_chat import translate_to_bengali
from bengali_tts import generate_bengali_audio

print("Report loaded")
router = APIRouter()


class ChatRequest(BaseModel):

    user_id: str
    message: str


@router.post("/chatbot")


async def chatbot_endpoint(request: ChatRequest):

    reply = await generate_chat_response(
        request.user_id,
        request.message
    )

    # =========================
    # SAVE CHAT HISTORY
    # =========================

    await chat_collection.insert_one({

        "user_id": request.user_id,

        "message": request.message,

        "reply": reply,

        "timestamp": datetime.utcnow()

    })

    return {
        "reply": reply
    }

@router.get("/download-report")

async def download_report(user_id: str):

    # =========================
    # GET RISK PREDICTION
    # =========================

    prediction = await cumulative_prediction(user_id)

    # =========================
    # GET LATEST PROFIT
    # =========================

    cursor = risk_data_collection.find(
        {"user_id": user_id}
    )

    data = await cursor.to_list(length=100)
    # Generate graphs

    risk_graph, profit_graph = generate_risk_profit_graphs(data)

    profit = None

    if data:

        latest = data[-1]

        profit = latest.get("Profit")

    # =========================
    # CREATE RISK RANKING
    # =========================

    risk_ranking = sorted(

        [
            ("Operational Risk",
             prediction.get("operational_risk")),

            ("Environmental Risk",
             prediction.get("environmental_risk")),

            ("Behavioral Risk",
             prediction.get("behavioral_risk")),

            ("Financial Risk",
             prediction.get("financial_risk"))

        ],

        key=lambda x: x[1],

        reverse=True

    )

    # =========================
    # BUSINESS STRENGTH SCORE
    # =========================

    overall = prediction.get("overall_risk", 0)

    strength_score = round(100 - overall)

    # =========================
    # GENERATE REPORT
    # =========================

    file_path =generate_business_report(

        prediction,
        profit,
        risk_ranking,
        strength_score,
        risk_graph,
        profit_graph

    )

    return FileResponse(

        file_path,

        media_type="application/pdf",

        filename="Business_Report.pdf"

    )

@router.get("/download-chat-history")

async def download_chat_history(user_id: str):

    # =========================
    # FETCH CHAT HISTORY
    # =========================

    cursor = chat_collection.find(
        {"user_id": user_id}
    )

    chat_data = await cursor.to_list(length=500)

    if not chat_data:

        return {
            "message":
            "No chat history available."
        }

    # =========================
    # GENERATE PDF
    # =========================

    file_path = generate_chat_history_report(
        chat_data
    )

    return FileResponse(

        file_path,

        media_type="application/pdf",

        filename="Chat_History_Report.pdf"

    )


@router.post("/translate")

async def translate_text(request: ChatRequest):

    try:

        # Step 1 — Translate text
        bengali_text = await translate_to_bengali(
            request.message
        )

        # Step 2 — Generate cached audio
        audio_file = generate_bengali_audio(
            bengali_text
        )

        # Send filename only
        audio_name = audio_file.split("\\")[-1]

        return {

            "reply": bengali_text,

            "audio_file": audio_name

        }

    except Exception as e:

        print("TRANSLATE ROUTE ERROR:", e)

        return {

            "reply": "Translation failed.",

            "audio_file": None

        }

@router.post("/speak-bengali")

async def speak_bengali(request: ChatRequest):

    audio_file = generate_bengali_audio(
        request.message
    )

    return FileResponse(

        audio_file,

        media_type="audio/mpeg",

        filename="bengali_voice.mp3"

    )