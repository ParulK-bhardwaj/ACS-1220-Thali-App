from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from thali_app.config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

###########################
# Authentication
###########################

#  Authentication Set up code
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

bcrypt = Bcrypt(app)

#  Main Blueprint

from thali_app.routes import main
app.register_blueprint(main)

with app.app_context(): 
    db.create_all()

# Auth Blueprint
from thali_app.routes import auth
app.register_blueprint(auth)

with app.app_context(): 
    db.create_all()