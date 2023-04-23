from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt
# from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm
from ..models import User

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    pass

@users.route("/login", methods=["GET", "POST"])
def login():
    pass

@users.route("/logout")
@login_required
def logout():
    pass