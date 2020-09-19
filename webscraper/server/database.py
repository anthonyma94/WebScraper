from webscraper.server import db
from flask_restful import fields
from flask_bcrypt import generate_password_hash, check_password_hash
import uuid, datetime


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    public_id = db.Column(
        db.String, nullable=False, default=str(uuid.uuid4()).replace("-", "")
    )

    def __init__(self, **kwargs):
        super(UserModel, self).__init__(**kwargs)
        self.hash_password()

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode("utf-8")

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)

    resource_fields = {
        "id": fields.String(attribute="public_id"),
        "username": fields.String,
        "email": fields.String,
        "password": fields.String,
        "date_created": fields.DateTime,
        "is_admin": fields.Boolean,
    }

    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}', password='{self.password}')>"


class ProductModel(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    upc = db.Column(db.Integer, unique=True)
    name = db.Column(db.String)

    resource_fields = {"name": fields.String}

    def __repr__(self) -> str:
        return f"<Product(name='{self.name}', id='{self.id}', upc='{self.upc}')>"
