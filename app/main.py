
import os
import re
from datetime import datetime, timezone

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.database import (
    check_database_connection,
    users_collection,
    blogs_collection,
    categories_collection
)

from app.auth import (
    hash_password,
    verify_password,
    normalize_role
)

from app.routes import users, blogs, categories, admin


load_dotenv()

VALID_ROLES = {"admin", "moderator", "writer"}

app = FastAPI(
    title="Blogify RBAC Blog Website",
    description="A Role-Based Access Control Blogging Platform",
    version="2.0.0"
)


app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "development-secret-change-me"),
    session_cookie="blogify_session",
    max_age=3600,
    same_site="lax",
    https_only=False
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

templates = Jinja2Templates(directory="app/templates")

app.include_router(users.router)
app.include_router(blogs.router)
app.include_router(categories.router)
app.include_router(admin.router)


# -------------------------
# HELPER FUNCTIONS
# -------------------------

def current_user(request: Request):
    user = request.session.get("user")

    if not user:
        return None

    user["role"] = normalize_role(user.get("role", "writer"))
    return user


def user_has_role(request: Request, *roles):
    user = current_user(request)

    return bool(user and user["role"] in roles)


def is_admin(request: Request):
    return user_has_role(request, "admin")


def is_moderator(request: Request):
    return user_has_role(request, "moderator")


def is_content_manager(request: Request):
    return user_has_role(request, "admin", "moderator")


def page(request: Request, template: str, **context):
    user = current_user(request)

    context["user"] = user
    context["is_admin"] = bool(user and user["role"] == "admin")
    context["is_moderator"] = bool(user and user["role"] == "moderator")
    context["is_writer"] = bool(user and user["role"] == "writer")
    context["can_create"] = bool(
        user and user["role"] in ["admin", "writer"]
    )
    context["can_manage_posts"] = bool(
        user and user["role"] in ["admin", "moderator"]
    )

    return templates.TemplateResponse(
        request=request,
        name=template,
        context=context
    )


def redirect(path: str):
    return RedirectResponse(url=path, status_code=303)


def admin_count():
    return users_collection.count_documents({"role": "admin"})


# -------------------------
# HOME PAGE
# -------------------------

@app.get("/")
def home(request: Request):
    blog_list = list(
        blogs_collection.find({"status": "published"})
        .sort("created_at", -1)
    )

    categories_list = list(
        categories_collection.find().sort("name", 1)
    )

    return page(
        request,
        "home.html",
        blogs=blog_list,
        categories=categories_list
    )


# -------------------------
# LOGIN
# -------------------------

@app.get("/login")
def login_page(request: Request):
    return page(request, "login.html", error=None)


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    email = email.lower().strip()

    account = users_collection.find_one({"email": email})

    if not account or not verify_password(
        password,
        account.get("password", "")
    ):
        return page(
            request,
            "login.html",
            error="Invalid email or password"
        )

    role = normalize_role(account.get("role", "writer"))

    # Upgrade old accounts from "user" to "writer"
    if account.get("role") != role:
        users_collection.update_one(
            {"_id": account["_id"]},
            {"$set": {"role": role}}
        )

    request.session.clear()

    request.session["user"] = {
        "id": str(account["_id"]),
        "name": account["name"],
        "email": account["email"],
        "role": role
    }

    if role in ["admin", "moderator"]:
        return redirect("/dashboard")

    return redirect("/blogs")


# -------------------------
# REGISTRATION
# -------------------------

@app.get("/register")
def register_page(request: Request):
    return page(request, "register.html", error=None)


@app.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    name = name.strip()
    email = email.lower().strip()

    if not name:
        return page(
            request,
            "register.html",
            error="Name is required"
        )

    if len(password) < 8:
        return page(
            request,
            "register.html",
            error="Password must contain at least 8 characters"
        )

    if users_collection.find_one({"email": email}):
        return page(
            request,
            "register.html",
            error="This email is already registered"
        )

    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": hash_password(password),
        "role": "writer",
        "created_at": datetime.now(timezone.utc)
    })

    return redirect("/login")


# -------------------------
# LOGOUT
# -------------------------

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return redirect("/")


# -------------------------
# BLOG LIST
# -------------------------

@app.get("/blogs")
def blogs_page(
    request: Request,
    search: str = "",
    category: str = ""
):
    user = current_user(request)

    # Public visitors see published posts only.
    # Admins and Moderators can see all posts.
    # Writers can see published posts and their own drafts.
    if user and user["role"] in ["admin", "moderator"]:
        query = {}
    elif user:
        query = {
            "$or": [
                {"status": "published"},
                {
                    "status": "draft",
                    "author_id": user["id"]
                }
            ]
        }
    else:
        query = {"status": "published"}

    if search:
        safe_search = re.escape(search)

        query["$and"] = query.get("$and", []) + [{
            "$or": [
                {"title": {"$regex": safe_search, "$options": "i"}},
                {"content": {"$regex": safe_search, "$options": "i"}},
                {"tags": {"$regex": safe_search, "$options": "i"}}
            ]
        }]

    if category:
        query["category"] = category

    blog_list = list(
        blogs_collection.find(query).sort("created_at", -1)
    )

    categories_list = list(
        categories_collection.find().sort("name", 1)
    )

    return page(
        request,
        "blogs.html",
        blogs=blog_list,
        categories=categories_list,
        search=search,
        selected_category=category
    )


# -------------------------
# CREATE BLOG
# Admin and Writer only
# -------------------------

@app.get("/blogs/new")
def add_blog_page(request: Request):
    if not current_user(request):
        return redirect("/login")

    if not user_has_role(request, "admin", "writer"):
        return redirect("/blogs")

    categories_list = list(
        categories_collection.find().sort("name", 1)
    )

    return page(
        request,
        "add_blog.html",
        categories=categories_list,
        error=None
    )


@app.post("/blogs/new")
def create_blog_page(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    tags: str = Form(""),
    image_url: str = Form(""),
    status: str = Form("draft")
):
    user = current_user(request)

    if not user:
        return redirect("/login")

    if user["role"] not in ["admin", "writer"]:
        return redirect("/blogs")

    if status not in ["draft", "published"]:
        status = "draft"

    blogs_collection.insert_one({
        "title": title.strip(),
        "content": content.strip(),
        "category": category.strip(),
        "tags": [
            tag.strip()
            for tag in tags.split(",")
            if tag.strip()
        ],
        "image_url": image_url.strip() or None,
        "status": status,
        "author": user["name"],
        "author_id": user["id"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })

    return redirect("/blogs")


# -------------------------
# EDIT BLOG
# Admin and Moderator only
# -------------------------

@app.get("/blogs/{blog_id}/edit")
def edit_blog_page(request: Request, blog_id: str):
    if not current_user(request):
        return redirect("/login")

    if not is_content_manager(request):
        return redirect("/blogs")

    if not ObjectId.is_valid(blog_id):
        return redirect("/blogs")

    blog = blogs_collection.find_one({
        "_id": ObjectId(blog_id)
    })

    if not blog:
        return redirect("/blogs")

    categories_list = list(
        categories_collection.find().sort("name", 1)
    )

    return page(
        request,
        "edit_blog.html",
        blog=blog,
        categories=categories_list
    )


@app.post("/blogs/{blog_id}/edit")
def update_blog_page(
    request: Request,
    blog_id: str,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    tags: str = Form(""),
    image_url: str = Form(""),
    status: str = Form("draft")
):
    if not current_user(request):
        return redirect("/login")

    if not is_content_manager(request):
        return redirect("/blogs")

    if not ObjectId.is_valid(blog_id):
        return redirect("/blogs")

    blog = blogs_collection.find_one({
        "_id": ObjectId(blog_id)
    })

    if not blog:
        return redirect("/blogs")

    if status not in ["draft", "published"]:
        status = "draft"

    blogs_collection.update_one(
        {"_id": ObjectId(blog_id)},
        {
            "$set": {
                "title": title.strip(),
                "content": content.strip(),
                "category": category.strip(),
                "tags": [
                    tag.strip()
                    for tag in tags.split(",")
                    if tag.strip()
                ],
                "image_url": image_url.strip() or None,
                "status": status,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    return redirect("/blogs")


# -------------------------
# DELETE BLOG
# Admin and Moderator only
# -------------------------

@app.post("/blogs/{blog_id}/delete")
def delete_blog_page(request: Request, blog_id: str):
    if not current_user(request):
        return redirect("/login")

    if not is_content_manager(request):
        return redirect("/blogs")

    if not ObjectId.is_valid(blog_id):
        return redirect("/blogs")

    blogs_collection.delete_one({
        "_id": ObjectId(blog_id)
    })

    return redirect("/blogs")


# -------------------------
# CATEGORIES
# Admin only for management
# -------------------------

@app.get("/categories")
def categories_page(request: Request):
    category_list = list(
        categories_collection.find().sort("name", 1)
    )

    return page(
        request,
        "categories.html",
        categories=category_list,
        error=None
    )


@app.post("/categories")
def create_category_page(
    request: Request,
    name: str = Form(...),
    description: str = Form("")
):
    if not current_user(request):
        return redirect("/login")

    if not is_admin(request):
        return redirect("/blogs")

    name = name.strip()

    if not name:
        return redirect("/categories")

    existing = categories_collection.find_one({
        "name": {
            "$regex": f"^{re.escape(name)}$",
            "$options": "i"
        }
    })

    if existing:
        category_list = list(
            categories_collection.find().sort("name", 1)
        )

        return page(
            request,
            "categories.html",
            categories=category_list,
            error="Category already exists"
        )

    categories_collection.insert_one({
        "name": name,
        "description": description.strip(),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })

    return redirect("/categories")


@app.post("/categories/{category_id}/delete")
def delete_category_page(request: Request, category_id: str):
    if not current_user(request):
        return redirect("/login")

    if not is_admin(request) or not ObjectId.is_valid(category_id):
        return redirect("/categories")

    categories_collection.delete_one({
        "_id": ObjectId(category_id)
    })

    return redirect("/categories")


# -------------------------
# DASHBOARD
# Admin and Moderator
# -------------------------

@app.get("/dashboard")
def dashboard_page(request: Request):
    user = current_user(request)

    if not user:
        return redirect("/login")

    if user["role"] == "writer":
        return redirect("/blogs")

    if user["role"] not in ["admin", "moderator"]:
        return redirect("/blogs")

    stats = {
        "total_blogs": blogs_collection.count_documents({}),
        "published_blogs": blogs_collection.count_documents({
            "status": "published"
        }),
        "draft_blogs": blogs_collection.count_documents({
            "status": "draft"
        }),
        "total_categories": categories_collection.count_documents({})
    }

    # Only Admin sees user management statistics and user list.
    if user["role"] == "admin":
        stats["total_users"] = users_collection.count_documents({})

        recent_users = list(
            users_collection.find({}, {"password": 0})
            .sort("created_at", -1)
            .limit(5)
        )
    else:
        stats["total_users"] = 0
        recent_users = []

    recent_blogs = list(
        blogs_collection.find()
        .sort("created_at", -1)
        .limit(5)
    )

    return page(
        request,
        "dashboard.html",
        stats=stats,
        blogs=recent_blogs,
        users=recent_users
    )


# -------------------------
# ADMIN USER MANAGEMENT PAGE
# Admin only
# -------------------------

@app.get("/admin/users")
def manage_users_page(request: Request):
    if not current_user(request):
        return redirect("/login")

    if not is_admin(request):
        return redirect("/blogs")

    user_list = list(
        users_collection.find({}, {"password": 0})
        .sort("created_at", -1)
    )

    return page(
        request,
        "users.html",
        users=user_list,
        error=None,
        success=None
    )


# -------------------------
# ADMIN: CREATE USER
# -------------------------

@app.post("/admin/users/create")
def admin_create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("writer")
):
    if not current_user(request):
        return redirect("/login")

    if not is_admin(request):
        return redirect("/blogs")

    name = name.strip()
    email = email.lower().strip()
    role = role.lower().strip()

    if role not in VALID_ROLES:
        return redirect("/admin/users")

    if not name or len(password) < 8:
        return redirect("/admin/users")

    if users_collection.find_one({"email": email}):
        return redirect("/admin/users")

    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": hash_password(password),
        "role": role,
        "created_at": datetime.now(timezone.utc)
    })

    return redirect("/admin/users")


# -------------------------
# ADMIN: CHANGE USER ROLE
# -------------------------

@app.post("/admin/users/{user_id}/role")
def admin_change_role(
    request: Request,
    user_id: str,
    role: str = Form(...)
):
    current = current_user(request)

    if not current:
        return redirect("/login")

    if current["role"] != "admin":
        return redirect("/blogs")

    if not ObjectId.is_valid(user_id):
        return redirect("/admin/users")

    role = role.lower().strip()

    if role not in VALID_ROLES:
        return redirect("/admin/users")

    target = users_collection.find_one({
        "_id": ObjectId(user_id)
    })

    if not target:
        return redirect("/admin/users")

    old_role = normalize_role(target.get("role", "writer"))

    # Prevent the last Admin from losing Admin access.
    if old_role == "admin" and role != "admin":
        if admin_count() <= 1:
            return redirect("/admin/users")

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": role}}
    )

    # Update the current session if the Admin changes their own role.
    if current["id"] == user_id:
        request.session.clear()

    return redirect("/admin/users")


# -------------------------
# ADMIN: DELETE USER
# -------------------------

@app.post("/admin/users/{user_id}/delete")
def admin_delete_user(request: Request, user_id: str):
    current = current_user(request)

    if not current:
        return redirect("/login")

    if current["role"] != "admin":
        return redirect("/blogs")

    if not ObjectId.is_valid(user_id):
        return redirect("/admin/users")

    # Admin cannot delete their own account.
    if current["id"] == user_id:
        return redirect("/admin/users")

    target = users_collection.find_one({
        "_id": ObjectId(user_id)
    })

    if not target:
        return redirect("/admin/users")

    target_role = normalize_role(target.get("role", "writer"))

    # Do not delete the last Admin account.
    if target_role == "admin" and admin_count() <= 1:
        return redirect("/admin/users")

    users_collection.delete_one({
        "_id": ObjectId(user_id)
    })

    return redirect("/admin/users")


# -------------------------
# HEALTH CHECK
# -------------------------

@app.get("/health")
def health():
    connected = check_database_connection()

    return {
        "application": "Blogify",
        "database": "connected" if connected else "disconnected"
    }
