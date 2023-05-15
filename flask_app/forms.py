from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, IMAGES
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
)
from . import photos

from .models import User


class SearchForm(FlaskForm):
    item_description = StringField(
        "Item Description", validators=[InputRequired(), Length(min=1, max=100)]
    )
    search_lost = SubmitField("Search lost items")
    search_found = SubmitField("Search found items")


class LostItemForm(FlaskForm):
    reference = TextAreaField("Reference")
    
    picture = FileField(
        "Picture",
        validators=[
            FileRequired(),
            #FileAllowed(UploadSet('photos', IMAGES), "Upload images only."),
            #FileAllowed(['jpg', 'png'], "Upload images only."),
            #FileAllowed(photos, "Upload images only."),
            FileAllowed(UploadSet('photos', IMAGES), "Upload images only.")
        ],
    )
    item_description = TextAreaField(
        "Item Description", validators=[InputRequired(), Length(min=5, max=500)]
    )
    location = TextAreaField(
        "Last Remembered Location", validators=[Length(min=5, max=500)]
    )
    submit = SubmitField("Submit Lost Item")


class FoundItemForm(FlaskForm):
    reference = TextAreaField("Reference")

    picture = FileField(
        "Picture",
        validators=[
            FileRequired(),
            #FileAllowed(photos, "Upload images only."),
            FileAllowed(UploadSet('photos', IMAGES), "Upload images only.")
        ],
    )
    item_description = TextAreaField(
        "Item Description", validators=[Length(min=5, max=500)]
    )
    location = TextAreaField(
        "Found Location", validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Submit Found Item")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")
        
    def validate_password(self, password):
        password = password.data
        if not any(c.isdigit() for c in password):
            raise ValidationError("You must have at least 1 number")
        
        if not ((any(c.isupper() for c in password)) or (any(c.islower() for c in password))):
            raise ValidationError("You must have at least 1 letter")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class UpdateUsernameForm(FlaskForm):
    new_username = StringField(
        "New Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Update Username")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")

class ChangePasswordForm(FlaskForm):
    new_password = PasswordField(
        "New Password", validators=[InputRequired(), Length(min=10, max=25)]
    )
    confirm_new_password = PasswordField(
        "Confirm New Password", validators=[InputRequired(), EqualTo("new_password")]
    )

    psubmit = SubmitField("Change Password")

    def validate_new_password(self, new_password):
        new_password = new_password.data

        if not any(c.isdigit() for c in new_password):
            raise ValidationError("You must have at least 1 number")
        
        if not ((any(c.isupper() for c in new_password)) or (any(c.islower() for c in new_password))):
            raise ValidationError("You must have at least 1 letter")

