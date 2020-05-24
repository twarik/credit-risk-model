from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Create a flask instance
app = Flask(__name__)
# suppress warning message
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Specify the database location (URI)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# Set the secret_key on our application to something unique and secret.
app.config['SECRET_KEY'] = '1b00c53097da10918fc60c2d4e48b938'
# Create instance of the database
db = SQLAlchemy(app)
# Initialise the Bcrypt class
bcrypt = Bcrypt(app)
# Initialise the LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from application import routes
