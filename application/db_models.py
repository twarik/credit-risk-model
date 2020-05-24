from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from application import db, login_manager, app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# create a class that represents the users table in the database
class User(db.Model, UserMixin):
    # define the table columns (fields)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# create a class that represents the debtors table in the database
class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(30), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(6), nullable=False)
    job = db.Column(db.String(30), nullable=False)
    housing = db.Column(db.String(6), nullable=False)
    saving = db.Column(db.String(15), nullable=False)
    checking = db.Column(db.String(10), nullable=False)
    credit = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(10), nullable=False)
    risk = db.Column(db.String(6), nullable=True)
    date_predicted = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"User('Housing:{self.housing}', 'Saving:{self.saving}', 'Credit:{self.credit}, 'Purpose:{self.purpose}')"
