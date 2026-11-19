
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Request

from app.database import users_collection
from app.schemas import UserRegister, UserLogin
from app.auth import (
    hash_password,
    verify_password,
    get_current_user,
    normalize_role
)

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


# USER REGISTRATION
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister):

    email = user.email.lower().strip()

    existing_user = users_collection.find_one({
        "email": email
    })

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    new_user = {
        "name": user.name.strip(),
        "email": email,
        "password": hash_password(user.password),
        "role": "writer",
        "created_at": datetime.now(timezone.utc)
    }

    result = users_collection.insert_one(new_user)

    return {
        "message": "Registration successful",
        "user_id": str(result.inserted_id),
        "name": new_user["name"],
        "email": email,
        "role": "writer"
    }


# USER LOGIN
@router.post("/login")
def login_user(user: UserLogin, request: Request):

    email = user.email.lower().strip()

    existing_user = users_collection.find_one({
        "email": email
    })

    if not existing_user or not verify_password(
        user.password,
        existing_user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Convert old "user" accounts to "writer"
    role = normalize_role(existing_user.get("role", "writer"))

    # Update old role in MongoDB
    if existing_user.get("role") != role:
        users_collection.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {"role": role}}
        )

    # Clear previous session
    request.session.clear()

    session_user = {
        "id": str(existing_user["_id"]),
        "name": existing_user["name"],
        "email": existing_user["email"],
        "role": role
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
