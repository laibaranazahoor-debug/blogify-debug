# Blogify – Role-Based Blogging Platform

## About the Project

Blogify is a full-stack blogging platform developed as part of my internship assignment. It allows users to register, log in, create and explore blog posts, while providing role-based access control to manage platform activities securely.

The application is built using **FastAPI**, **MongoDB Atlas**, **HTML**, **CSS**, **JavaScript**, and **Jinja2**. It includes user authentication, blog and category management, an admin dashboard, and separate permissions for Admin, Moderator, and Writer roles.

## Features

### 1. User Authentication
- User registration and login
- Secure password hashing
- Session-based authentication
- User logout
- Role-based access control (RBAC)
- Protected pages and operations

### 2. Role-Based Access Control

Blogify supports three user roles:

| Feature | Admin | Moderator | Writer |
|---|---|---|---|
| Create blog posts | Yes | No | Yes |
| View blog posts | Yes | Yes | Yes |
| Edit blog posts | Yes | Yes | No |
| Delete blog posts | Yes | Yes | No |
| Manage users | Yes | No | No |
| Change user roles | Yes | No | No |
| Access admin dashboard | Yes | Yes | No |

Permissions are enforced on the server side, not only by hiding frontend buttons.

### 3. Blog Management
- Create new blog posts
- View published blogs
- Save posts as drafts
- Publish blog posts
- Edit and delete posts according to user permissions
- Add categories, tags, and image URLs
- Search by title, content, and tags
- Filter posts by category

### 4. Category Management
- Create categories
- View available categories
- Delete categories through the management interface
- Manage categories through API endpoints

### 5. Admin Panel and User Management
- Role-based dashboard access
- View registered users
- View total blogs and categories
- View published posts and drafts
- Create user accounts
- Change user roles
- Delete users
- Protect important administrative operations

### 6. Frontend
- Modern neon-inspired interface
- Dark and light themes
- Multiple theme options
- Theme preference saved in the browser
- Responsive layout
- Dynamic pages using Jinja2 templates

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
| Uvicorn | Application server |
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
│   │   ├── register.html
│   │   └── users.html
│   │
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   └── schemas.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/laibaranazahoor-debug/blogify-debug.git
```

### 2. Open the Project Folder

```bash
cd blogify-debug
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

Create a `.env` file in the main project directory and configure your MongoDB Atlas connection:

```env
MONGODB_URL=your_mongodb_atlas_connection_string
DATABASE_NAME=blogify_database
SECRET_KEY=your_secure_secret_key
```

Replace the placeholder values with your own credentials.

**Security Note:** Never upload your actual `.env` file, database credentials, or secret keys to GitHub.

### 7. Run the Application

```bash
python -m uvicorn app.main:app --reload --port 8000
```

## Application URLs

After starting the application locally:

| Page | URL |
|---|---|
| Home | http://127.0.0.1:8000/ |
| Login | http://127.0.0.1:8000/login |
| Register | http://127.0.0.1:8000/register |
| Blogs | http://127.0.0.1:8000/blogs |
| Create Blog | http://127.0.0.1:8000/blogs/new |
| Categories | http://127.0.0.1:8000/categories |
| Dashboard | http://127.0.0.1:8000/dashboard |
| User Management | http://127.0.0.1:8000/admin/users |
| API Documentation | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

## API Endpoints

### Users

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/users/register` | Register a new user |
| POST | `/api/users/login` | Login user |
| GET | `/api/users/me` | Get current user details |
| POST | `/api/users/logout` | Logout user |

### Blogs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/blogs/` | Create a blog |
| GET | `/api/blogs/` | Get published blogs |
| GET | `/api/blogs/mine` | Get current user's blogs |
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

The administrative interface provides dashboard statistics and user management. Administrative API routes are available through the application.

Refer to `/docs` for the registered API routes and their request details.

## Database

MongoDB Atlas is used as the cloud database.

The main collections are:

- `users` – Stores user information, password hashes, and roles.
- `blogs` – Stores blog posts, authors, categories, tags, and publication status.
- `categories` – Stores blog categories and descriptions.

## Learning Outcomes

During this project, I gained practical experience in:

- Building REST APIs with FastAPI
- Connecting applications to MongoDB Atlas
- Implementing authentication and role-based authorization
- Performing CRUD operations
- Working with Jinja2 templates
- Developing dynamic frontend pages
- Managing environment variables
- Organizing a modular backend application
- Implementing Admin, Moderator, and Writer permissions

## Project Status

Blogify is an internship project featuring a blogging platform with user authentication, role-based access control, blog and category management, user administration, and a responsive frontend.

---

**Developed by:** Laiba Zahoor  
**Project:** Blogify – Role-Based Blogging Platform  
**Technologies:** Python, FastAPI, MongoDB Atlas, HTML, CSS, JavaScript, and Jinja2