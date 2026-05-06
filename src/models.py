from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()
BLOCKS = ["theory", "algorithms", "data", "backend", "frontend"]


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)
    about = db.Column(db.String, nullable=True)
    email = db.Column(db.String, index=True, unique=True, nullable=True)
    hashed_password = db.Column(db.String, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"User <{self.name}>"


class Task(db.Model, UserMixin):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    block = db.Column(db.String, nullable=False)
    order = db.Column(db.Integer, default=0)
    difficulty = db.Column(db.String, default='easy')
    check_type = db.Column(db.String, nullable=False)
    expected_answer = db.Column(db.Text, nullable=True)
    test_cases = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"Task <{self.title}>"