import os
from pymongo import MongoClient
from bson import ObjectId

MONGO_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGO_URI)
db = client["llm_chatbot"]

class Transcription:
    def __init__(self, filename, transcript, transcript_id,summary):
        self.filename = filename
        self.transcript = transcript
        self.transcript_id =transcript_id
        self.summary= summary

    def to_dict(self):
        return {
            "filename": self.filename,
            "transcript": self.transcript,
            "transcript_id": self.transcript_id,
            "summary": self.summary 
        }

def save_transcription(transcription):
    transcription_collection = db["transcriptions"]
    return transcription_collection.insert_one(transcription.to_dict()).inserted_id

def get_transcription(transcript_id):
    transcription_collection = db["transcriptions"]
    return transcription_collection.find_one({"_id": ObjectId(transcript_id)})
