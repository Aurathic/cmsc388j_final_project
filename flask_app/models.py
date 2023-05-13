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
    # circular dependency so was crashing
    #found_item = db.ReferenceField(FoundItem)


class FoundItem(db.Document):
    person = db.ReferenceField(User, required=True)
    description = db.StringField(min_length=5, max_length=500)
    location = db.StringField(required=True, min_length=5, max_length=500)
    lost_item = db.ReferenceField(LostItem)
    item_pic = db.ImageField(required=True)
    time = db.DateTimeField(required=True) 

LostItem.found_item = db.ReferenceField(FoundItem)