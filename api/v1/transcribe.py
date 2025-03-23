# import os
# import openai
# from fastapi import APIRouter, UploadFile, HTTPException
# from pymongo import MongoClient
# from dotenv import load_dotenv

# load_dotenv()

# # MongoDB setup
# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client["llm_chatbot"]
# transcription_collection = db["transcriptions"]

# router = APIRouter()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# @router.post("/transcribe")
# async def transcribe_audio(file: UploadFile):
#     try:
#         # Save audio file temporarily
#         file_path = f"temp/{file.filename}"
#         with open(file_path, "wb") as buffer:
#             buffer.write(await file.read())

#         # Use Whisper API to transcribe audio
#         openai.api_key = OPENAI_API_KEY
#         audio_file = open(file_path, "rb")
#         transcript_data = openai.Audio.transcribe("whisper-1", audio_file)

#         # Save to MongoDB
#         transcription_entry = {
#             "filename": file.filename,
#             "transcript": transcript_data["text"],
#         }
#         transcription_collection.insert_one(transcription_entry)

#         return {"message": "Transcription successful", "transcript": transcript_data["text"]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")
#     finally:
#         os.remove(file_path)


import os
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
from api.v1.auth import get_current_user
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import certifi
import uuid

load_dotenv()

# ✅ MongoDB setup
MONGO_URL = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())
db = client["llm_chatbot"]
transcription_collection = db["transcriptions"]

router = APIRouter()

# ✅ Deepgram API Setup
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)  # Correct initialization ✅

# ✅ API Endpoint: Transcribe and store in DB
@router.post("/transcribe")
async def transcribe_audio(file: UploadFile, current_user: dict = Depends(get_current_user)):
    try:
        # ✅ Create temp directory if not exists
        os.makedirs("temp", exist_ok=True)

        # ✅ Save audio file temporarily
        file_path = f"temp/{file.filename}"
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(await file.read())

        # ✅ Read audio file correctly using synchronous open()
        with open(file_path, "rb") as audio:
            # ✅ Create the payload for transcription
            payload: FileSource = {"buffer": audio}

            # ✅ Set transcription options
            options = PrerecordedOptions(
                smart_format=True,
                model="nova-2",  # Use latest Deepgram model
                language="en-US"  # Set language to US English
            )

            print("Requesting transcript...")
            print("Your file may take up to a couple of minutes to process...")

            # ✅ For larger files, increase timeout to 300 seconds (5 mins)
            response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options, timeout=300)

            # ✅ Print response (optional for debugging)
            # print(response.to_json(indent=4))

        # ✅ Check if transcription is successful
        if "results" not in response.to_dict() or "channels" not in response.to_dict()["results"]:
            raise HTTPException(status_code=500, detail="Invalid Deepgram response")

        # ✅ Extract transcription text
        transcript_data = response.to_dict()["results"]["channels"][0]["alternatives"][0]["transcript"]

        # ✅ Generate a unique transcript ID
        transcript_id = str(uuid.uuid4())

        # ✅ Generate summary if requested
        summary_data = "Summary not available"
        try:
            # ✅ Use same payload and options for summary
            summary_options = PrerecordedOptions(
                smart_format=True,
                model="nova-2",
                language="en-US",
                summarize="v2"  # ✅ Generate summary
            )
            summary_response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, summary_options, timeout=300)

            # ✅ Check if summary is available
            if "results" in summary_response.to_dict() and "channels" in summary_response.to_dict()["results"]:
                summary_data = summary_response.to_dict()["results"]["channels"][0]["alternatives"][0].get("summary", "Summary not available")

        except Exception as summary_error:
            print(f"Summary generation error: {str(summary_error)}")
            summary_data = "Summary not available"

        # ✅ Save transcription and summary to MongoDB
        # print(current_user)
        transcription_entry = {
            "transcript_id": transcript_id,
            "filename": file.filename,
            "transcript": transcript_data,
            "summary": summary_data,
            "user_id": current_user["username"]
        }
        transcription_collection.insert_one(transcription_entry)

        # ✅ Return success response
        return {
            "transcript_id": transcript_id,
            "message": "Transcription successful",
            "transcript": transcript_data,
            "summary": summary_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")

    finally:
        # ✅ Clean up the temporary file after processing
        if os.path.exists(file_path):
            os.remove(file_path)
