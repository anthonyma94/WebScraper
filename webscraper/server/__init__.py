from functools import wraps
from flask import Flask
from flask_restful import Api, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims
import asyncio


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///../../database.db"
app.config["JWT_SECRET_KEY"] = "super-oh-so-secret"
app.config["JWT_ERROR_MESSAGE_KEY"] = "message"
api = Api(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
loop = asyncio.get_event_loop()


def addToDatabase(items):
    if not isinstance(items, list):
        db.session.add(items)
    else:
        for i in items:
            db.session.add(i)
    db.session.commit()


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if "admin" not in claims:
            abort(403, message="Unauthorized")
        else:
            return f(*args, **kwargs)

    return wrapper