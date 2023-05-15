import base64
import io
from flask_login import UserMixin
from . import db, login_manager
from . import config

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)

    # Returns unique string identifying our object
    def get_id(self):
        return self.username


class LostItem(db.Document):
    person = db.ReferenceField(User, required=True)
    description = db.StringField(required=True, min_length=5, max_length=500)
    location = db.StringField(min_length=5, max_length=500)
    item_pic = db.ImageField(required=False)
    time = db.DateTimeField(required=True)
    #found_item = db.ReferenceField(FoundItem)
    reference = db.GenericReferenceField()

    @property
    def b64_image(self):
        print(self.item_pic)
        if self.item_pic:
            file = self.item_pic
        else:
            file = open("flask_app/static/noimagedefault.png", "rb")
        image_bytes = io.BytesIO(file.read())
        image = base64.b64encode(image_bytes.getvalue()).decode()
        return image


class FoundItem(db.Document):
    person = db.ReferenceField(User, required=True)
    description = db.StringField(min_length=5, max_length=500)
    location = db.StringField(required=True, min_length=5, max_length=500)
    item_pic = db.ImageField(required=True)
    time = db.DateTimeField(required=True) 
    #lost_item = db.ReferenceField(LostItem)
    reference = db.GenericReferenceField()

    def b64_image(self):
        print(self.item_pic)
        if self.item_pic:
            file = self.item_pic
        else:
            file = open("flask_app/static/noimagedefault.png", "rb")
        image_bytes = io.BytesIO(file.read())
        image = base64.b64encode(image_bytes.getvalue()).decode()
        return image

#FoundItem.lost_item = db.ReferenceField(LostItem)
#LostItem.found_item = db.ReferenceField(FoundItem)