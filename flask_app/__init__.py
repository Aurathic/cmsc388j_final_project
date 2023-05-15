#imports
from flask import Flask, render_template, request, redirect, url_for
from flask_talisman import Talisman
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.utils import secure_filename
from PIL import Image
#from flaskext.uploads import UploadSet, configure_uploads

# Global variables 
db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()

photos = UploadSet('photos', IMAGES)

# import routes of blueprints
from .users.routes import users
from .posts.routes import posts

def page_not_found(e):
    return render_template("404.html", title='Page not found', error=e), 404

def create_app(test_config=None):
    app = Flask(__name__)
    '''
    csp = {
        'default-src': ['\'self\''],
        'script-src': ['\'self\'', '*code.jquery.com/*', '*cdn.jsdelivr.net/*'],
        'style-src': ['\'self\'', '*bootstrapcdn.com/*']
    }
    '''
    csp = {
        'default-src': [
            '\'self\'',
            #'\'unsafe-inline\'',
            'stackpath.bootstrapcdn.com',
            'code.jquery.com',
            'cdn.jsdelivr.net'
        ],
        'img-src': '*'
    }



    Talisman(app, content_security_policy=csp)
    #Talisman(app, content_security_policy=csp, content_security_policy_report_uri='https://127.0.0.1:5000/csp_reports')
    #Talisman(app)
    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_error_handler(404, page_not_found)


    app.config['UPLOADED_PHOTOS_DEST'] = '.'
    
    configure_uploads(app, (photos,))
    
    login_manager.login_view = "users.login"

    return app
