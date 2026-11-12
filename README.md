# Blogify – Blogging Platform with Admin Panel

## About the Project

Blogify is a blogging platform that I developed as part of my internship task. The main purpose of this project is to create a platform where users can register, log in, write blogs, manage their posts and explore content shared by others.

I used FastAPI for the backend, MongoDB Atlas for database storage and HTML, CSS, JavaScript and Jinja2 for the frontend. I also added an admin panel to manage the platform and view important statistics.

## Features

### User Authentication
- User registration and login
- Secure password hashing
- Session-based authentication
- User logout
- Different access levels for users and admins

### Blog Management
- Create new blogs
- View published blogs
- Edit and delete your own blogs
- Save blogs as drafts
- Publish blogs
- Add categories, tags and image URLs
- Search blogs by title, content and tags
- Filter blogs by category

### Category Management
- Create categories
- View available categories
- Delete categories through the admin panel
- Manage categories through API endpoints

### Admin Panel
- Admin-only dashboard
- View total registered users
- View total blogs
- Check published blogs and drafts
- View total categories
- View recent blogs and registered users
- Manage blog content through admin API endpoints

### Frontend
- Modern neon-inspired interface
- Multiple themes
- Dark and light appearance options
- Theme preference saved in the browser
- Responsive layout for different screen sizes
- Jinja2 templates for dynamic pages

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | Backend framework |
| MongoDB Atlas | Cloud database |
| PyMongo | MongoDB connection |
| HTML | Page structure |
| CSS | Styling and themes |
| JavaScript | Frontend interactions |
| Jinja2 | Dynamic HTML rendering |
| Uvicorn | Local development server |
| Pydantic | Data validation |

## Project Structure

```text
Blogify/
│
├── app/
│   ├── routes/
│   │   ├── admin.py
│   │   ├── blogs.py
│   │   ├── categories.py
│   │   └── users.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── images/
│   │   └── js/
│   │       └── main.js
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── dashboard.html
│   │   ├── blogs.html
│   │   ├── add_blog.html
│   │   ├── edit_blog.html
│   │   ├── categories.html
│   │   ├── login.html
│   │   └── register.html
│   │
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   └── schemas.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the Project Folder

```bash
cd blogify
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the main project folder and add your MongoDB Atlas connection details.

```env
MONGODB_URL=your_mongodb_atlas_connection_string
DATABASE_NAME=blogify_database
SECRET_KEY=your_secure_secret_key
```

Replace the placeholder values with your own configuration.

**Note:** Never upload your actual `.env` file or database credentials to GitHub.

### 7. Run the Application

```bash
python -m uvicorn app.main:app --reload --port 8000
```

## Application URLs

After running the application locally, you can access:

| Page | URL |
|---|---|
| Home | http://127.0.0.1:8000/ |
| Login | http://127.0.0.1:8000/login |
| Register | http://127.0.0.1:8000/register |
| Blogs | http://127.0.0.1:8000/blogs |
| Create Blog | http://127.0.0.1:8000/blogs/new |
| Categories | http://127.0.0.1:8000/categories |
| Admin Dashboard | http://127.0.0.1:8000/dashboard |
| API Documentation | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

## API Endpoints

### Users

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/users/register` | Register a new user |
| POST | `/api/users/login` | Login user |
| GET | `/api/users/me` | Get current user |
| POST | `/api/users/logout` | Logout user |

### Blogs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/blogs/` | Create a blog |
| GET | `/api/blogs/` | Get all published blogs |
| GET | `/api/blogs/mine` | Get your blogs |
| GET | `/api/blogs/{blog_id}` | Get a specific blog |
| PUT | `/api/blogs/{blog_id}` | Update a blog |
| DELETE | `/api/blogs/{blog_id}` | Delete a blog |

### Categories

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/categories/` | Create a category |
| GET | `/api/categories/` | Get all categories |
| GET | `/api/categories/{category_id}` | Get a specific category |
| PUT | `/api/categories/{category_id}` | Update a category |
| DELETE | `/api/categories/{category_id}` | Delete a category |

### Admin

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/dashboard` | Get dashboard statistics |
| GET | `/api/admin/users` | Get all users |
| GET | `/api/admin/blogs` | Get all blogs |
| PUT | `/api/admin/blogs/{blog_id}/status` | Update blog status |
| DELETE | `/api/admin/blogs/{blog_id}` | Delete a blog |

## Database

I used MongoDB Atlas as the cloud database for this project.

The main collections are:

- `users` – Stores registered user information and password hashes.
- `blogs` – Stores blog posts, categories, tags and publication status.
- `categories` – Stores blog categories and their descriptions.

## Learning Outcomes

While developing Blogify, I got practical experience with:

- Building REST APIs using FastAPI
- Connecting Python applications with MongoDB Atlas
- Implementing user authentication and authorization
- Performing CRUD operations
- Working with Jinja2 templates
- Creating dynamic frontend pages
- Managing environment variables
- Organizing a backend project into separate modules

## Project Status

This project was developed as an internship assignment. It includes the blogging API, user authentication, category management and an admin dashboard with a Jinja2-based frontend.

---

**Developed by:** Laiba Zahoor  
**Project:** Blogify – Blogging Platform with Admin Panel  
**Technology:** FastAPI, Python, MongoDB Atlas and Jinja2