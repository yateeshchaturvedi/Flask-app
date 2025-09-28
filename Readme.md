# Flask Book App: Project & User Flow Documentation

This document outlines the structure, technology stack, user roles, and operational flow of the **Flask Book App**, a role-based web application for managing a book inventory.

---

## 1. Project Overview

The Flask Book App is a **role-based web application** designed for book management. Access and functionality are determined by the user's role.

### User Roles

| Role | Description |
| :--- | :--- |
| **Public** | Can view books without logging in. |
| **Viewer** | Can log in and view books. |
| **Admin** | Can log in, manage books (add/edit/delete), and create other admins. |

### Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Flask, SQLAlchemy, Flask-Login | Web framework, ORM, and user session management. |
| **Frontend** | Jinja2, HTML, Bootstrap | Templating engine for dynamic and responsive UI. |
| **Database** | PostgreSQL | Robust relational database. |
| **Deployment** | Docker & Docker Compose | Containerization for easy setup and consistency. |

---

## 2. Folder Structure

The project follows a standard Flask application structure.

```mermaid
flowchart TD
    A[app/] --> A1[__init__.py<br>App factory, DB setup]
    A --> A2[models.py<br>SQLAlchemy models (User, Book)]
    A --> A3[routes.py<br>Routes for UI, API, admin]
    A --> A4[templates/]
    A4 --> T1[base.html]
    A4 --> T2[books.html]
    A4 --> T3[add_book.html]
    A4 --> T4[edit_book.html]
    A4 --> T5[create_admin.html]
    A4 --> T6[login.html]
    A4 --> T7[register.html]
    A --> A5[static/ <br>CSS, JS (optional)]
    B[Dockerfile]
    C[docker-compose.yml]
    D[requirements.txt <br>Python dependencies]
    E[run.py <br>Application entry point]

    root[Project Root] --> A
    root --> B
    root --> C
    root --> D
    root --> E
```


---

## 3. Database Structure

The application uses two primary tables: `Users` and `Books`.

### Users Table

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `int` | Primary key |
| `username` | `string` | Username |
| `email` | `string` | Email address |
| `password_hash` | `string` | **Hashed password** (security is mandatory) |
| `role` | `string` | `admin` or `viewer` |

### Books Table

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `int` | Primary key |
| `title` | `string` | Book title |
| `author` | `string` | Book author |

---

## 4. User Roles & Access

This table details the permissions for each user role.

| Role | Login Required? | Can View Books? | Can Add/Edit/Delete Books? | Can Create Admin? |
| :--- | :--- | :--- | :--- | :--- |
| **Public** | ❌ | ✅ | ❌ | ❌ |
| **Viewer** | ✅ | ✅ | ❌ | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ |

---

## 5. Docker Setup

The application is containerized using Docker Compose for a self-contained development and deployment environment.

### `docker-compose.yml` Example

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: booksdb
    ports:
      - "5432:5432" # Host:Container

  web:
    build: .
    depends_on:
      - db
    ports:
      - "5000:5000" # Host:Container
    environment:
      # These variables allow the Flask app to connect to the 'db' service
      POSTGRES_HOST: db 
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: booksdb
```
### Start Containers
Use the following command to build the Flask image, start the database, and run the application in detached mode:
```Bash
docker-compose up --build -d
```
## 6. Initial User Setup
After starting the containers, you must create the initial Admin and Viewer users using the Flask shell.

Step 1: Open Flask Shell
Find the container name (e.g., flask-book-app-web-1) and execute a shell session:

```Bash

docker exec -it <web-container-name> flask shell
```
Step 2: Create Admin and Viewer Users
Run this Python code inside the Flask shell to commit the default users to the database:

```Python

from app.models import db, User

# First Admin
admin = User(username="admin", email="admin@example.com", role="admin")
admin.set_password("admin123")
db.session.add(admin)

# First Viewer
viewer = User(username="viewer", email="viewer@example.com", role="viewer")
viewer.set_password("viewer123")
db.session.add(viewer)

db.session.commit()
print("Initial users created!")
```

### Initial Login Credentials
| Role   | Username | Password   |
|--------|----------|------------|
| Admin  | admin    | admin123   |
| Viewer | viewer   | viewer123  |


## 7. Frontend & Templates
The Jinja2 templates handle the application's presentation and user experience, with a focus on role-based dynamic content.

| Template               | Purpose                  | Dynamic Logic                                           |
|------------------------|--------------------------|--------------------------------------------------------|
| base.html              | Master layout            | Dynamic navbar based on `current_user` role.          |
| books.html             | Book list page           | Admins see Add/Edit/Delete buttons; others do not.    |
| add_book.html / edit_book.html | Forms             | Exclusively accessible and visible to Admins.        |
| create_admin.html      | Admin creation form      | Exclusively accessible and visible to Admins.        |
| login.html / register.html | Authentication        | Standard user login and registration forms.          |



### Navbar Logic
| Role    | Navbar Options                        |
|---------|---------------------------------------|
| Public  | Books, Login, Register                |
| Viewer  | Books, Logout                         |
| Admin   | Books, Add Book, Create Admin, Logout |


## 8. Application Flow
The core application flow is centered around viewing and managing books, with access control enforced by Flask-Login.

**Entry Point:**  
A user opens `/ui/books` and sees the list of books.

**Public User:**  
- Can only view the list.  
- All modification routes are inaccessible.

**Viewer User:**  
- Logs in.  
- Can view books.  
- Blocked from all management routes (e.g., `/ui/add`).

**Admin User:**  
- Logs in and has full management access:  
  - Add new books: `/ui/add`  
  - Edit books: `/ui/edit/<id>`  
  - Delete books: `/ui/delete/<id>`  
  - Create new admins: `/admin/create`

**Session Management:**  
- Handled by Flask-Login using `current_user` to check role and authentication status.

**Data Interaction:**  
- Flask + SQLAlchemy manage all database queries and transactions.


## 9. Notes & Best Practices
✅ Always use hashed passwords (implemented via set_password in the models).

✅ The first admin must be created manually before additional users can be registered or created.

✅ Ensure public and viewer users are never rendered admin-specific UI elements or given access to admin routes.

✅ Use Docker Compose to keep the development environment consistent and simplify setup.

Optional Enhancement: Add a database connection retry loop to the Flask app's startup to prevent "connection refused" errors when the database container initializes slower than the web container.