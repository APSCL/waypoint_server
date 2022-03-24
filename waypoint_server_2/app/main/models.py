from flask_sqlalchemy import SQLAlchemy
from app import db

class TestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return f"User:{self.id} - {self.name}"