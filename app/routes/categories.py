
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import categories_collection
from app.schemas import CategoryCreate
from app.auth import require_admin


router = APIRouter(
    prefix="/api/categories",
    tags=["Categories"]
)


def serialize_category(category):
    category["id"] = str(category.pop("_id"))
    return category


# CREATE CATEGORY - ADMIN ONLY
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    admin=Depends(require_admin)
):

    name = category.name.strip()

    if categories_collection.find_one({
        "name": {"$regex": f"^{name}$", "$options": "i"}
    }):
        raise HTTPException(
            status_code=409,
            detail="Category already exists"
        )

    new_category = {
        "name": name,
        "description": category.description,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    result = categories_collection.insert_one(new_category)

    saved_category = categories_collection.find_one({
        "_id": result.inserted_id
    })

    return {
        "message": "Category created successfully",
        "category": serialize_category(saved_category)
    }


# GET ALL CATEGORIES - PUBLIC
@router.get("/")
def get_categories():

    categories = categories_collection.find().sort("name", 1)

    return {
        "total": categories_collection.count_documents({}),
        "categories": [
            serialize_category(category)
            for category in categories
        ]
    }


# GET SINGLE CATEGORY - PUBLIC
@router.get("/{category_id}")
def get_category(category_id: str):

    if not ObjectId.is_valid(category_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid category ID"
        )

    category = categories_collection.find_one({
        "_id": ObjectId(category_id)
    })

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return serialize_category(category)


# UPDATE CATEGORY - ADMIN ONLY
@router.put("/{category_id}")
def update_category(
    category_id: str,
    category_data: CategoryCreate,
    admin=Depends(require_admin)
):

    if not ObjectId.is_valid(category_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid category ID"
        )

    existing_category = categories_collection.find_one({
        "_id": ObjectId(category_id)
    })

    if not existing_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    name = category_data.name.strip()

    duplicate = categories_collection.find_one({
        "name": {"$regex": f"^{name}$", "$options": "i"},
        "_id": {"$ne": ObjectId(category_id)}
    })

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Category name already exists"
        )

    categories_collection.update_one(
        {"_id": ObjectId(category_id)},
        {
            "$set": {
                "name": name,
                "description": category_data.description,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    updated_category = categories_collection.find_one({
        "_id": ObjectId(category_id)
    })

    return {
        "message": "Category updated successfully",
        "category": serialize_category(updated_category)
    }


# DELETE CATEGORY - ADMIN ONLY
@router.delete("/{category_id}")
def delete_category(
    category_id: str,
    admin=Depends(require_admin)
):

    if not ObjectId.is_valid(category_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid category ID"
        )

    existing_category = categories_collection.find_one({
        "_id": ObjectId(category_id)
    })

    if not existing_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    categories_collection.delete_one({
        "_id": ObjectId(category_id)
    })

    return {
        "message": "Category deleted successfully"
    }
