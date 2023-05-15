from enum import Enum
import json
import os
import time
from flask_mail import Message
from cv2 import FileStorage
from flask import Blueprint, render_template, url_for, redirect, request, flash, Response
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from urllib import request


from ..models import User, LostItem, FoundItem
from ..forms import *
from .. import camera, mail
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

    #print("\n\n",FoundItem.objects,"\n\n",)
    #print("\n\n",LostItem.objects,"\n\n",)
    
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
        
        # handle camera data
        camera_img = form.hidden_image.data
        # handle picture data
        file_img = form.picture.data

        print(form.hidden_image)
        print(camera_img, "CAM")
        print(file_img, "FILE")
   
        if camera_img is not None:
            print('camera image not none!')
            # save data uri to image
            with request.urlopen(camera_img) as response:
                data = response.read()
            with open('image.png', 'wb') as f:
                f.write(data)

            f = open('image.png', 'rb')
            item.item_pic.replace(f, content_type='png')
        elif file_img is not None:
            print('image not none!')
            print(file_img)
            filename = secure_filename(file_img.filename)
            content_type = f'images/{filename[-3:]}'
            item.item_pic.replace(file_img.stream, content_type=content_type)

        item.save()

        # Update the reference in the other object
        if reference_item is not None:
            reference_item.reference = item
            reference_item.save()

            #after successful update, send email about post
            other_user = reference_item.person
            other_user_email = other_user.email
            other_user_username = other_user.username

            subject = 'Your item has been claimed' if item_type == "lost" else 'Your item has been found'
            body_text = ""

            if item_type == "lost":
                subject = 'Your item has been claimed'
                body_text = 'Hello ' + str(other_user_username)  \
                + ',\n\nThis is a notification that your posted item was claimed. ' \
                + 'Your item description: \n' \
                + str(reference_item.description)
            else:
                subject = 'Your item has been found'
                body_text = 'Hello ' + str(other_user_username)  \
                + ',\n\nThis is a notification that your posted item was found.\n\n ' \
                + 'Your item description: \n' \
                + str(reference_item.description)


            msg = Message(subject,
                sender="lostandfound31415@gmail.com",
                recipients=[other_user_email])
            msg.body = body_text
            mail.send(msg)            

        return redirect(url_for("posts.item", item_type=item_type, item_id=item.id))

    return render_template(f"items/new_item.html", form=form, item_type=item_type)


@posts.route("/item/<item_type>/<item_id>", methods=["GET", "POST"])
def item(item_type, item_id=None):
    # Pass in lost item object from DB
    if item_type == 'lost':
        item = LostItem.objects(id=item_id).first()
    else:
        item = FoundItem.objects(id=item_id).first()
    
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

@posts.route('/capture',methods=['POST'])
def capture():
    item_type="lost"
    reference=None
   # print(item_type, reference)
    #print(request, request.get_json())
    data = json.loads(request.data)
    #print(data)
    image_data = data['image_data']

    # Define the path to save the image
    image_path = 'captured_image.png'

    # Save the captured image to a file
    save_image(image_data)

    # Create and populate form field
    form = LostItemForm() if item_type == "lost" else FoundItemForm()
    form.image_file.data = FileStorage(filename=image_path)
    
    #print(form)
    #return render_template(f"items/new_item.html", form=form, item_type=item_type, reference=reference)
    
    return 'Image captured and saved'

def save_image(image_data, image_path):
    # Decode the base64-encoded image data
    _, encoded = image_data.split(',', 1)
    image_bytes = base64.b64decode(encoded)

    # Save the image to the specified path
    with open(image_path, 'wb') as f:
        f.write(image_bytes)

    