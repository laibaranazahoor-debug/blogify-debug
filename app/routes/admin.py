
from bson import ObjectId
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Body

from app.database import (
    users_collection,
    blogs_collection,
    categories_collection
)
from app.auth import require_admin


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Panel"]
)


# ADMIN DASHBOARD
@router.get("/dashboard")
def admin_dashboard(admin=Depends(require_admin)):

    return {
        "message": "Admin dashboard data fetched successfully",
        "statistics": {
            "total_users": users_collection.count_documents({}),
            "total_blogs": blogs_collection.count_documents({}),
            "published_blogs": blogs_collection.count_documents({
                "status": "published"
            }),
            "draft_blogs": blogs_collection.count_documents({
                "status": "draft"
            }),
            "total_categories": categories_collection.count_documents({})
        }
    }


# GET ALL USERS
@router.get("/users")
def get_all_users(admin=Depends(require_admin)):

    users = users_collection.find(
        {},
        {"password": 0}
    ).sort("created_at", -1)

    user_list = []

    for user in users:
        user["id"] = str(user.pop("_id"))
        user_list.append(user)

    return {
        "total": len(user_list),
        "users": user_list
    }


# GET ALL BLOGS INCLUDING DRAFTS
@router.get("/blogs")
def get_all_admin_blogs(admin=Depends(require_admin)):

    blogs = blogs_collection.find().sort("created_at", -1)

    blog_list = []

    for blog in blogs:
        blog["id"] = str(blog.pop("_id"))
        blog_list.append(blog)

    return {
        "total": len(blog_list),
        "blogs": blog_list
    }


# UPDATE BLOG STATUS
@router.put("/blogs/{blog_id}/status")
def update_blog_status(
    blog_id: str,
    new_status: Literal["draft", "published"] = Body(..., embed=True),
    admin=Depends(require_admin)
):

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

    blogs_collection.update_one(
        {"_id": ObjectId(blog_id)},
        {
            "$set": {
                "status": new_status
            }
        }
    )

    return {
        "message": f"Blog status changed to {new_status}"
    }


# DELETE ANY BLOG
@router.delete("/blogs/{blog_id}")
def admin_delete_blog(
    blog_id: str,
    admin=Depends(require_admin)
):

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

    blogs_collection.delete_one({
        "_id": ObjectId(blog_id)
    })

    return {
        "message": "Blog deleted successfully by admin"
    }
