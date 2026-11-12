
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Request

from app.database import users_collection
from app.schemas import UserRegister, UserLogin
from app.auth import hash_password, verify_password, get_current_user

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


# USER REGISTRATION
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister):

    existing_user = users_collection.find_one({
        "email": user.email.lower()
    })

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    new_user = {
        "name": user.name,
        "email": user.email.lower(),
        "password": hash_password(user.password),
        "role": "user",
        "created_at": datetime.now(timezone.utc)
    }

    result = users_collection.insert_one(new_user)

    return {
        "message": "Registration successful",
        "user_id": str(result.inserted_id),
        "name": user.name,
        "email": user.email.lower(),
        "role": "user"
    }


# USER LOGIN
@router.post("/login")
def login_user(user: UserLogin, request: Request):

    existing_user = users_collection.find_one({
        "email": user.email.lower()
    })

    if not existing_user or not verify_password(
        user.password,
        existing_user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    session_user = {
        "id": str(existing_user["_id"]),
        "name": existing_user["name"],
        "email": existing_user["email"],
        "role": existing_user["role"]
    }

    request.session["user"] = session_user

    return {
        "message": "Login successful",
        "user": session_user
    }


# GET CURRENT USER
@router.get("/me")
def current_user(request: Request):

    user = get_current_user(request)

    return {
        "message": "User details fetched successfully",
        "user": user
    }


# USER LOGOUT
@router.post("/logout")
def logout_user(request: Request):

    if not request.session.get("user"):
        raise HTTPException(
            status_code=401,
            detail="You are not logged in"
        )

    request.session.clear()

    return {
        "message": "Logout successful"
    }
