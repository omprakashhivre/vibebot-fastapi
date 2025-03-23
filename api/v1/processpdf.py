import os
import aiofiles # type: ignore
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
from api.v1.auth import get_current_user
from deepgram import DeepgramClient, PrerecordedOptions, FileSource # type: ignore
from PyPDF2 import PdfReader # type: ignore
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
deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)  # Correct for Deepgram v3

# ✅ API Endpoint: Process PDF and Store in DB
@router.post("/process-pdf")
async def process_pdf(file: UploadFile, current_user: dict = Depends(get_current_user)):
    try:
        # ✅ Create temp directory if not exists
        os.makedirs("temp", exist_ok=True)

        # ✅ Save PDF file temporarily
        file_path = f"temp/{file.filename}"
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(await file.read())

        # ✅ Read and extract text from PDF
        pdf_text = extract_text_from_pdf(file_path)

        # ✅ Check if PDF text is extracted properly
        if not pdf_text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")

        # ✅ Generate a unique transcript ID for PDF content
        transcript_id = str(uuid.uuid4())

        # ✅ Use Deepgram to summarize the extracted text
        # summary_data = generate_summary_with_deepgram(pdf_text)

        # ✅ Save PDF data and summary to MongoDB
        pdf_entry = {
            "transcript_id": transcript_id,
            "filename": file.filename,
            "transcript": pdf_text,
            # "summary": summary_data,
            "user_id": current_user["username"]
        }
        transcription_collection.insert_one(pdf_entry)

        # ✅ Return success response
        return {
            "transcript_id": transcript_id,
            "message": "PDF processing successful",
            "transcript": pdf_text,
            # "summary": summary_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during PDF processing: {str(e)}")

    finally:
        # ✅ Remove the temp file after processing
        if os.path.exists(file_path):
            os.remove(file_path)


# ✅ Helper Function: Extract Text from PDF
def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        # Open and read the PDF
        pdf_reader = PdfReader(pdf_path)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
        return text_content
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


# ✅ Helper Function: Generate Summary with Deepgram
def generate_summary_with_deepgram(text: str) -> str:
    try:
        # ✅ Create payload for Deepgram summarization
        payload: FileSource = {"buffer": text.encode("utf-8")}

        # ✅ Set options for Deepgram summarization
        options = PrerecordedOptions(
            smart_format=True,
            model="nova-2",  # ✅ Use Deepgram model for summarization
            language="en-US",
            summarize="v2"  # ✅ Request summarization from Deepgram
        )

        # ✅ Call Deepgram API to summarize the text
        summary_response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options, timeout=300)

        # ✅ Extract summary if available
        summary_data = (
            summary_response.to_dict()["results"]["channels"][0]["alternatives"][0].get("summary", "Summary not available")
        )
        return summary_data

    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return "Summary not available"
