
import os
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
from app.auth import hash_password, verify_password
from app.routes import users, blogs, categories, admin

load_dotenv()

app = FastAPI(
    title="Blogify API",
    description="A Modern Blogging Platform with Neon Admin Panel",
    version="1.0.0"
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


def current_user(request: Request):
    return request.session.get("user")


def is_admin(request: Request):
    user = current_user(request)
    return bool(user and user.get("role") == "admin")


def page(request: Request, template: str, **context):
    context["user"] = current_user(request)
    context["is_admin"] = is_admin(request)
    return templates.TemplateResponse(
        request=request,
        name=template,
        context=context
    )


def redirect(path: str):
    return RedirectResponse(url=path, status_code=303)


@app.get("/")
def home(request: Request):
    blogs = list(
        blogs_collection.find({"status": "published"})
        .sort("created_at", -1)
    )
    categories_list = list(categories_collection.find().sort("name", 1))

    return page(
        request,
        "home.html",
        blogs=blogs,
        categories=categories_list
    )


@app.get("/login")
def login_page(request: Request):
    return page(request, "login.html", error=None)


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    account = users_collection.find_one({"email": email.lower().strip()})

    if not account or not verify_password(password, account["password"]):
        return page(
            request,
            "login.html",
            error="Invalid email or password"
        )

    request.session["user"] = {
        "id": str(account["_id"]),
        "name": account["name"],
        "email": account["email"],
        "role": account.get("role", "user")
    }

    return redirect("/dashboard" if account.get("role") == "admin" else "/blogs")


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
    email = email.lower().strip()

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
        "name": name.strip(),
        "email": email,
        "password": hash_password(password),
        "role": "user",
        "created_at": datetime.now(timezone.utc)
    })

    return redirect("/login")


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return redirect("/")


@app.get("/blogs")
def blogs_page(
    request: Request,
    search: str = "",
    category: str = ""
):
    query = {}

    if not is_admin(request):
        query["status"] = "published"

    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]

    if category:
        query["category"] = category

    blog_list = list(
        blogs_collection.find(query).sort("created_at", -1)
    )
    categories_list = list(categories_collection.find().sort("name", 1))

    return page(
        request,
        "blogs.html",
        blogs=blog_list,
        categories=categories_list,
        search=search,
        selected_category=category
    )


@app.get("/blogs/new")
def add_blog_page(request: Request):
    if not current_user(request):
        return redirect("/login")

    categories_list = list(categories_collection.find().sort("name", 1))
    return page(request, "add_blog.html", categories=categories_list, error=None)


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

    if status not in ["draft", "published"]:
        status = "draft"

    blogs_collection.insert_one({
        "title": title.strip(),
        "content": content.strip(),
        "category": category.strip(),
        "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
        "image_url": image_url.strip() or None,
        "status": status,
        "author": user["name"],
        "author_id": user["id"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })

    return redirect("/blogs")


@app.get("/blogs/{blog_id}/edit")
def edit_blog_page(request: Request, blog_id: str):
    user = current_user(request)

    if not user:
        return redirect("/login")

    if not ObjectId.is_valid(blog_id):
        return redirect("/blogs")

    blog = blogs_collection.find_one({"_id": ObjectId(blog_id)})

    if not blog:
        return redirect("/blogs")

    if blog.get("author_id") != user["id"] and user.get("role") != "admin":
        return redirect("/blogs")

    categories_list = list(categories_collection.find().sort("name", 1))

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
    user = current_user(request)

    if not user or not ObjectId.is_valid(blog_id):
        return redirect("/blogs")

    blog = blogs_collection.find_one({"_id": ObjectId(blog_id)})

    if not blog:
        return redirect("/blogs")

    if blog.get("author_id") != user["id"] and user.get("role") != "admin":
        return redirect("/blogs")

    if status not in ["draft", "published"]:
        status = "draft"

    blogs_collection.update_one(
        {"_id": ObjectId(blog_id)},
        {"$set": {
            "title": title.strip(),
            "content": content.strip(),
            "category": category.strip(),
            "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
            "image_url": image_url.strip() or None,
            "status": status,
            "updated_at": datetime.now(timezone.utc)
        }}
    )

    return redirect("/blogs")


@app.post("/blogs/{blog_id}/delete")
def delete_blog_page(request: Request, blog_id: str):
    user = current_user(request)

    if not user or not ObjectId.is_valid(blog_id):
        return redirect("/blogs")

    blog = blogs_collection.find_one({"_id": ObjectId(blog_id)})

    if blog and (
        blog.get("author_id") == user["id"]
        or user.get("role") == "admin"
    ):
        blogs_collection.delete_one({"_id": ObjectId(blog_id)})

    return redirect("/blogs")


@app.get("/categories")
def categories_page(request: Request):
    category_list = list(categories_collection.find().sort("name", 1))
    return page(request, "categories.html", categories=category_list, error=None)


@app.post("/categories")
def create_category_page(
    request: Request,
    name: str = Form(...),
    description: str = Form("")
):
    if not is_admin(request):
        return redirect("/login")

    name = name.strip()

    if categories_collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}}):
        category_list = list(categories_collection.find().sort("name", 1))
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
    if not is_admin(request) or not ObjectId.is_valid(category_id):
        return redirect("/categories")

    categories_collection.delete_one({"_id": ObjectId(category_id)})
    return redirect("/categories")


@app.get("/dashboard")
def dashboard_page(request: Request):
    if not is_admin(request):
        return redirect("/login")

    stats = {
        "total_users": users_collection.count_documents({}),
        "total_blogs": blogs_collection.count_documents({}),
        "published_blogs": blogs_collection.count_documents({"status": "published"}),
        "draft_blogs": blogs_collection.count_documents({"status": "draft"}),
        "total_categories": categories_collection.count_documents({})
    }

    recent_blogs = list(
        blogs_collection.find().sort("created_at", -1).limit(5)
    )

    recent_users = list(
        users_collection.find({}, {"password": 0})
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


@app.get("/health")
def health():
    connected = check_database_connection()
    return {
        "application": "Blogify",
        "database": "connected" if connected else "disconnected"
    }
