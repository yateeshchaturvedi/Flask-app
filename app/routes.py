from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from .models import db, User, Book
from functools import wraps

main = Blueprint("main", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


# --- Auth ---

@main.route("/admin/create", methods=["GET", "POST"])
@admin_required
def create_admin():
    """
    Admin-only route to create new admin users.
    Only accessible by existing admins.
    """
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if username/email already exists
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists")
            return redirect(url_for("main.create_admin"))

        # Create new admin user
        user = User(username=username, email=email, role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f"Admin user '{username}' created successfully!")
        return redirect(url_for("main.list_users"))

    return render_template("create_admin.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("main.register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully. Please log in.")
        return redirect(url_for("main.login"))
    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.books_ui"))
        flash("Invalid username or password")
        return redirect(url_for("main.login"))
    return render_template("login.html")

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully")
    return redirect(url_for("main.login"))

# --- Book CRUD ---
@main.route("/ui/books")
def books_ui():
    sort_order = request.args.get("sort", "asc").lower()
    from sqlalchemy import asc, desc
    books = Book.query.order_by(desc(Book.id) if sort_order=="desc" else asc(Book.id)).all()
    return render_template("books.html", books=books, sort_order=sort_order)

@main.route("/ui/add", methods=["GET", "POST"])
@admin_required
def add_book_form():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        new_book = Book(title=title, author=author)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("main.books_ui"))
    return render_template("add_book.html")

@main.route("/ui/edit/<int:book_id>", methods=["GET", "POST"])
@admin_required
def edit_book_form(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == "POST":
        book.title = request.form["title"]
        book.author = request.form["author"]
        db.session.commit()
        return redirect(url_for("main.books_ui"))
    return render_template("edit_book.html", book=book)

@main.route("/ui/delete/<int:book_id>")
@admin_required
def delete_book_ui(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("main.books_ui"))
