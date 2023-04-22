#imports
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# import routes of blueprints
from .users.routes import users
from .posts.routes import posts

# variables 
db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()

def page_not_found(e):
    return render_template("404.html"), 404

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py", silent=False)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # register blueprints
    app.register_blueprint(users)
    app.register_blueprint(posts)

    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app
