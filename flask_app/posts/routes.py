from enum import Enum
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)

from ..models import User, LostItem, FoundItem
from ..forms import *

# other imports
import io
import base64
import datetime


posts = Blueprint('posts', __name__)

@posts.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        item_type = 'lost' if 'search_lost' in str(request.form) \
            else 'found' # 'Search found items'
        print("\n"*2, request.form, "\n"*2, item_type, "\n"*2)
        return redirect(url_for("posts.query", 
                                query=form.item_description.data, 
                                item_type=item_type))

    return render_template("index.html",form=form)

@posts.route("/query/<item_type>/<query>", methods=["GET", "POST"])
def query(query, item_type):
    # Find results associated with query:
    # Find all (lost,found) items which have *not* been associated with a (found,lost) item
    # and contain the query as a substring in their description
    if item_type == 'lost':
        results = LostItem.objects(found_item__exists=False, description__icontains=query)
    elif item_type == 'found':
        results = FoundItem.objects(lost_item__exists=False, description__icontains=query)
    else:
        results = None
    # Display
    return render_template("query.html", results=results, item_type=item_type)



@posts.route('/new/lost_item', defaults={'reference': None}, methods=["GET", "POST"])
@posts.route("/new/lost_item/<reference>", methods=["GET", "POST"])
def new_lost_item(reference):
    # TODO: Pass in previous fields
    form = LostItemForm()

    if form.validate_on_submit() and current_user.is_authenticated:
        lost_item = LostItem(
            person = current_user._get_current_object(),
            description = form.item_description.data,
            location = form.location.data, 
            time = datetime.datetime.now,
            found_item = None,
            item_pic = None
        )
        # handle picture data
        img = form.picture.data
        if img is not None:
            filename = secure_filename(img.filename)
            content_type = f'images/{filename[-3:]}'
            lost_item.item_pic.replace(img.stream, content_type=content_type)

        lost_item.save()
        return redirect(url_for("posts.index")) # temporary change this
    
    return render_template("items/new_lost_item.html", form=form)

@posts.route('/new/found_item', defaults={'reference': None})
@posts.route("/new/found_item/<reference>", methods=["GET", "POST"])
def new_found_item(reference):
    # TODO: Pass in previous fields
    form = FoundItemForm()

    return render_template("items/new_found_item.html", form=form)


@posts.route("/item/<item_type>/<item_id>", methods=["GET", "POST"])
def item(item_type, item_id=None):
    # Pass in lost item object from DB
    if item_type == 'lost':
        item = LostItem.objects(id=item_id).first()
    else:
        item = FoundItem.objects(id=item_id).first()
    print(item)
    return render_template("items/found_item.html", item=item)

"""
@posts.route("/lost_item/<item_id>", methods=["GET", "POST"])
def lost_item(item_id=None):
    # Pass in found item object from DB
    
    return render_template("items/lost_item.html", item=item)

@posts.route("/found_item/<item_id>", methods=["GET", "POST"])
def found_item(item_id=None):
    # Pass in lost item object from DB
    item = FoundItem.objects(id=item_id).first()
    print(item)
    return render_template("items/found_item.html", item=item)
"""