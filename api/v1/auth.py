import os
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from models.user import UserCreate, UserLogin
from utils.auth import get_password_hash, verify_password, create_access_token, decode_access_token
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

router = APIRouter()

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["llm_chatbot"]
user_collection = db["users"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


# ✅ Register New User
@router.post("/register")
async def register(user: UserCreate):
    existing_user = user_collection.find_one({"username": user.username})

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
    }
    user_collection.insert_one(user_data)
    return {"message": "User registered successfully"}


# ✅ User Login and Get Token
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print("==> Login api called...")
    user_data = user_collection.find_one(
        {"$or": [{"username": form_data.username}, {"email": form_data.username}]}
    )

    if not user_data or not verify_password(form_data.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user_data["username"]})
    return {"access_token": access_token, "token_type": "bearer", "username": user_data["username"]}


# ✅ Get Current User from Token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    username = decode_access_token(token)

    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token or token expired")

    user_data = user_collection.find_one({"username": username})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    return user_data


@router.get("/verify-token")
async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        print("==> Verifying token...")
        username = decode_access_token(token)

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token or token expired")

        user_data = user_collection.find_one({"username": username}, {"password": 0})  # Exclude password

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Return user details except password with isValid flag
        user_data["_id"] = str(user_data["_id"])  # Convert ObjectId to string
        return {
            "isValid": True,
            "user": user_data,
        }
    except Exception as e:
        print(f"Token verification failed: {str(e)}")
        return {"isValid": False, "detail": "Invalid or expired token"}