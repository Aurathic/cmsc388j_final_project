from enum import Enum
import json
import os
import time
from flask import Blueprint, render_template, url_for, redirect, request, flash, Response
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)

from ..models import User, LostItem, FoundItem
from ..forms import *
from .. import camera
import cv2

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
    results=None
    print('check1')
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
            print('image not none!')
            filename = secure_filename(img.filename)
            content_type = f'images/{filename[-3:]}'
            item.item_pic.replace(img.stream, content_type=content_type)

        item.save()

        # Update the reference in the other object
        if reference_item is not None:
            reference_item.reference = item
            reference_item.save()

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


#### OPENCV STUFF ####
# Adapted from https://towardsdatascience.com/camera-app-with-flask-and-opencv-bd147f6c0eec


"""
@posts.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():  # generate frame by frame from camera
    global out, capture, rec_frame
    while True:
        success, frame = camera.read() 
        print(success, frame)
        if success:
            capture=0
            now = datetime.datetime.now()
            p = os.path.sep.join(['shots', "shot_{}.png".format(str(now).replace(":",''))])
            cv2.imwrite(p, frame)
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass

@posts.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST':
    
        global capture
        capture=1
    elif request.method=='GET':
        return render_template('index.html')
    return render_template('index.html')
"""

"""
def generate():
    while True:
        # Capture a frame from the webcam
        ret, frame = camera.read()
        if not ret:
            break

        # Convert the frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        # Yield the frame to the client as a Flask response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@posts.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
"""

@posts.route('/capture',methods=['POST','GET'])
def capture():
    data = json.loads(request.data)
    image_data = data['image_data']

    # Save the captured image to a file
    save_image(image_data)

    return 'Image captured and saved'

def save_image(image_data):
    # Decode the base64-encoded image data
    _, encoded = image_data.split(',', 1)
    image_bytes = base64.b64decode(encoded)

    # Define the path to save the image
    image_path = 'captured_image.png'

    # Save the image to the specified path
    with open(image_path, 'wb') as f:
        f.write(image_bytes)