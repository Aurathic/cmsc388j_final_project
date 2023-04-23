from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)

from ..models import User, Post
# from ..forms import 

posts = Blueprint('posts', __name__)

@posts.route("/", methods=["GET", "POST"])
def index():
    #form = SearchForm()

    #if form.validate_on_submit():
    #    return redirect(url_for("movies.query_results", query=form.search_query.data))

    return render_template("index.html")