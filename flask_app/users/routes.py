from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, ChangePasswordForm
from .. import bcrypt, mail

from ..models import User, LostItem, FoundItem

users = Blueprint("users", __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("movies.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        user.save()

        msg = Message("Account creation",
            sender="lostandfound31415@gmail.com",
            recipients=[form.email.data])
        msg.body = 'Hello ' + str(form.username.data) + ',\n\nThis is a confirmation you are now registered as a user on Lost and Found.'
        mail.send(msg)

        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("posts.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("users.account"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("posts.index"))

@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    username_form = UpdateUsernameForm()
    password_form = ChangePasswordForm()

    if username_form.validate_on_submit():
        # current_user.username = username_form.username.data
        current_user.modify(username=username_form.new_username.data)
        current_user.save()

        flash('Username successfully updated. Please login with your new username.')
        return redirect(url_for("users.login"))
    
    if password_form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(password_form.new_password.data).decode("utf-8")
        current_user.modify(password=hashed)
        current_user.save()
        logout_user()
        flash('Password successfully updated. Please login with your new password.')
        return redirect(url_for("users.login"))        

    return render_template("user_account.html", 
                           title="Account",
                           uname_form=username_form,
                           pw_form=password_form)

@users.route("/user/<username>")
def user_profile(username):
    user = None
    try:
        user = User.objects(username=username).first()
        if user is None:
            raise Exception('The user you are looking for doesn\'t exist.')
    except Exception as e:
        return render_template("user_profile.html", error_msg=str(e))   

    username = user.get_id()

    # pull all user posts
    lost_results = LostItem.objects(person=user)
    found_results = FoundItem.objects(person=user)
    return render_template("user_profile.html", username=username, lost_results=lost_results, found_results=found_results)

'''
# debugging talisman only
import json
@users.route("/csp_reports", methods=['POST'])
def csp_reports():
    print('reaching this method')
    content = request.get_json(force=True)
    print(json.dumps(content, indent=4, sort_keys=True))
'''
