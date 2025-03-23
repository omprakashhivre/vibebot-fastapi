from fastapi import FastAPI, UploadFile, File
from api.v1.transcribe import transcribe_audio
from api.v1.chat import ask_question
from api.v1.transcripts import get_all_transcripts
from api.v1 import transcribe
from api.v1 import chat
from api.v1 import transcripts
from api.v1 import processpdf
from api.v1.auth import router as auth_router
from fastapi.openapi.models import APIKey
from fastapi.openapi.models import SecurityScheme
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="LLM & ASR Chatbot API",
    description="Transcribe audio/video and chat with AI using OpenAI/LangChain",
    version="1.0.0",
)

origins = [    
    "*",                      
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to LLM Chatbot API!"}

# Transcription Endpoint
app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
app.include_router(transcribe.router, prefix="/api/v1", tags=["Transcription"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(processpdf.router, prefix="/api/v1", tags=["PDFProcess"])

# app.post("/api/v1/transcribe")(transcribe_audio)

# # Chat Endpoint
# app.post("/api/v1/chat")(ask_question)
app.include_router(transcripts.router, prefix="/api/v1" , tags=["Transcription"])
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="LLM Chatbot API",
        version="1.0.0",
        description="API to handle audio transcription and querying using LLMs with secure JWT auth.",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi