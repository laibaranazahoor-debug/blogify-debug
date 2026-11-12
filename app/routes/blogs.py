
import re
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request, status

from app.database import blogs_collection
from app.schemas import BlogCreate, BlogUpdate
from app.auth import get_current_user


router = APIRouter(
    prefix="/api/blogs",
    tags=["Blogs"]
)


# Convert MongoDB document into JSON-friendly response
def serialize_blog(blog):
    blog["id"] = str(blog.pop("_id"))
    return blog


# CREATE BLOG
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_blog(blog: BlogCreate, request: Request):

    user = get_current_user(request)

    new_blog = blog.model_dump()

    new_blog["author_id"] = user["id"]
    new_blog["author_name"] = user["name"]
    new_blog["created_at"] = datetime.now(timezone.utc)
    new_blog["updated_at"] = datetime.now(timezone.utc)

    result = blogs_collection.insert_one(new_blog)

    saved_blog = blogs_collection.find_one({
        "_id": result.inserted_id
    })

    return {
        "message": "Blog created successfully",
        "blog": serialize_blog(saved_blog)
    }


# GET ALL PUBLISHED BLOGS
@router.get("/")
def get_all_blogs(
    search: Optional[str] = None,
    category: Optional[str] = None
):

    query = {"status": "published"}

    if search:
        safe_search = re.escape(search)
        query["$or"] = [
            {"title": {"$regex": safe_search, "$options": "i"}},
            {"content": {"$regex": safe_search, "$options": "i"}},
            {"tags": {"$regex": safe_search, "$options": "i"}}
        ]

    if category:
        query["category"] = category

    blogs = blogs_collection.find(query).sort(
        "created_at", -1
    )

    return {
        "total": blogs_collection.count_documents(query),
        "blogs": [serialize_blog(blog) for blog in blogs]
    }


# GET MY BLOGS INCLUDING DRAFTS
@router.get("/mine")
def get_my_blogs(request: Request):

    user = get_current_user(request)

    query = {"author_id": user["id"]}

    blogs = blogs_collection.find(query).sort(
        "created_at", -1
    )

    return {
        "total": blogs_collection.count_documents(query),
        "blogs": [serialize_blog(blog) for blog in blogs]
    }


# GET SINGLE BLOG
@router.get("/{blog_id}")
def get_blog(blog_id: str, request: Request):

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid blog ID"
        )

    blog = blogs_collection.find_one({
        "_id": ObjectId(blog_id)
    })

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    user = request.session.get("user")

    if blog["status"] != "published":
        if not user or (
            user["id"] != blog["author_id"]
            and user["role"] != "admin"
        ):
            raise HTTPException(
                status_code=403,
                detail="You cannot access this draft"
            )

    return serialize_blog(blog)


# UPDATE BLOG
@router.put("/{blog_id}")
def update_blog(
    blog_id: str,
    blog_data: BlogUpdate,
    request: Request
):

    user = get_current_user(request)

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid blog ID"
        )

    existing_blog = blogs_collection.find_one({
        "_id": ObjectId(blog_id)
    })

    if not existing_blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    if (
        existing_blog["author_id"] != user["id"]
        and user["role"] != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot edit this blog"
        )

    update_data = blog_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No update data provided"
        )

    update_data["updated_at"] = datetime.now(timezone.utc)

    blogs_collection.update_one(
        {"_id": ObjectId(blog_id)},
        {"$set": update_data}
    )

    updated_blog = blogs_collection.find_one({
        "_id": ObjectId(blog_id)
    })

    return {
        "message": "Blog updated successfully",
        "blog": serialize_blog(updated_blog)
    }


# DELETE BLOG
@router.delete("/{blog_id}")
def delete_blog(blog_id: str, request: Request):

    user = get_current_user(request)

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid blog ID"
        )

    existing_blog = blogs_collection.find_one({
        "_id": ObjectId(blog_id)
    })

    if not existing_blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    if (
        existing_blog["author_id"] != user["id"]
        and user["role"] != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot delete this blog"
        )

    blogs_collection.delete_one({
        "_id": ObjectId(blog_id)
    })

    return {
        "message": "Blog deleted successfully"
    }
