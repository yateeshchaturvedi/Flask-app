from flask import Flask
from flask_login import LoginManager
from .models import db

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecret"

    # DB config
    import os
    DB_USER = os.environ.get("POSTGRES_USER", "postgres")
    DB_PASS = os.environ.get("POSTGRES_PASSWORD", "postgres")
    DB_NAME = os.environ.get("POSTGRES_DB", "newsdb")
    DB_HOST = os.environ.get("POSTGRES_HOST", "db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = "main.login"
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    return app
