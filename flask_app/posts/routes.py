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

from flask_uploads import UploadSet, configure_uploads, IMAGES


posts = Blueprint('posts', __name__)

@posts.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        item_type = 'lost' if 'search_lost' in str(request.form) \
            else 'found' # 'Search found items'
        #print("\n"*2, request.form, "\n"*2, item_type, "\n"*2)
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
        results = LostItem.objects(reference__exists=False, description__icontains=query)
    elif item_type == 'found':
        results = FoundItem.objects(reference__exists=False, description__icontains=query)
    else:
        results = None
    # Display
    return render_template("query.html", results=results, item_type=item_type)

@posts.route('/new/<item_type>', defaults={'reference': None}, methods=["GET", "POST"])
@posts.route("/new/<item_type>/<reference>", methods=["GET", "POST"])
def new(item_type, reference):
    # TODO: Pass in previous fields
    form = LostItemForm() if item_type == "lost" else FoundItemForm()

    print("\n\n",FoundItem.objects,"\n\n",)
    print("\n\n",LostItem.objects,"\n\n",)
    
    if form.validate_on_submit() and current_user.is_authenticated:
        # Find the associated reference
        reference_item = reference and (
            FoundItem.objects(id=reference).first() if item_type == "lost"
            else LostItem.objects(id=reference).first())
        
        # New object parameters
        params = {
            "person": current_user._get_current_object(),
            "description": form.item_description.data,
            "location": form.location.data, 
            "time": datetime.datetime.now,
            "reference": reference_item,
            "item_pic": None
        }
        item = LostItem(**params) if item_type == "lost" else FoundItem(**params) 
        
        # handle picture data
        img = form.picture.data
        if img is not None:
            filename = secure_filename(img.filename)
            content_type = f'images/{filename[-3:]}'
            item.item_pic.replace(img.stream, content_type=content_type)

        item.save()

        # Update the reference in the other object
        reference_item.reference = item

        return redirect(url_for("posts.item", item_type=item_type, item_id=item.id))

    return render_template(f"items/new_item.html", form=form, item_type=item_type)


@posts.route("/item/<item_type>/<item_id>", methods=["GET", "POST"])
def item(item_type, item_id=None):
    # Pass in lost item object from DB
    if item_type == 'lost':
        item = LostItem.objects(id=item_id).first()
    else:
        item = FoundItem.objects(id=item_id).first()
    
    # Get the associated reference object if it exists (?) 
    
    
    return render_template(f"items/item.html", item_type=item_type, item=item)


################# Helper ####################
def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image