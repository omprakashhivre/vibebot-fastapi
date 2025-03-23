import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from api.v1.auth import get_current_user
from utils.llm import query_llm

router = APIRouter()

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["llm_chatbot"]
transcription_collection = db["transcriptions"]

# Request model
class ChatRequest(BaseModel):
    transcript_id: str
    question: str


@router.post("/chat")
async def ask_question(request: ChatRequest, current_user=Depends(get_current_user)):
    try:
        # Fetch the transcript from MongoDB
        transcript_entry = transcription_collection.find_one({"transcript_id": request.transcript_id})

        if not transcript_entry:
            raise HTTPException(status_code=404, detail="Transcript not found")

        transcript_text = transcript_entry["transcript"]

        # ✅ Call Deepgram Nova API to get the answer
        answer = await query_llm(transcript_text, request.question)

        # Return the question and answer
        return {"question": request.question, "answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during LLM query: {str(e)}")
