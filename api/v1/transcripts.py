from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
import os

from api.v1.auth import get_current_user

load_dotenv()

router = APIRouter()

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["llm_chatbot"]
transcription_collection = db["transcriptions"]


@router.get("/transcripts")
async def get_all_transcripts(current_user=Depends(get_current_user)):
    try:
        # Fetch all transcriptions from the database
        transcripts = transcription_collection.find({}, {"_id": 0})
        
        # Convert cursor to list
        transcripts_list = list(transcripts)

        if not transcripts_list:
            return {"message": "No transcripts found"}

        return {"transcripts": transcripts_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transcripts: {str(e)}")
