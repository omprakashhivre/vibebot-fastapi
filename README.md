# 🚀 LLM Chatbot with ASR - FastAPI Backend

This is a **FastAPI backend** for an AI-powered chatbot with Automatic Speech Recognition (ASR) functionality using **Deepgram API** and MongoDB for data storage. The backend transcribes audio, generates text responses, and securely handles user authentication.

---

## 📑 **Table of Contents**
- [🔧 Features](#-features)
- [⚡️ Tech Stack](#️-tech-stack)
- [📦 Prerequisites](#-prerequisites)
- [🚀 Installation](#-installation)
- [▶️ Running the Application](#-running-the-application)
- [🔑 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [💡 Environment Variables](#-environment-variables)
- [📝 Contribution Guidelines](#-contribution-guidelines)
- [📜 License](#-license)

---

## 🔧 **Features**
✅ Transcribe audio and video files using Deepgram API  
✅ Secure user authentication with JWT tokens  
✅ Store transcripts and metadata in MongoDB  
✅ Fast and asynchronous API responses  
✅ Error handling and validation using Pydantic models  
✅ CORS-enabled for frontend communication  

---

## ⚡️ **Tech Stack**
- **Backend:** FastAPI, Python 3.13  
- **Database:** MongoDB with Pymongo  
- **Auth:** JWT Authentication  
- **Transcription API:** Deepgram SDK  
- **Web Server:** Uvicorn  

---

## 📦 **Prerequisites**

Make sure you have the following installed:
- [Python 3.13+](https://www.python.org/downloads/)
- [MongoDB](https://www.mongodb.com/try/download/community) running locally or remotely
- [Node.js (for Next.js frontend)](https://nodejs.org/)
- `pip` package manager for installing dependencies

---

## 🚀 **Installation**

### 1. **Clone the Repository**
```bash
git clone https://github.com/omprakashhivre/vibebot-fastapi
cd /vibebot-fastapi
