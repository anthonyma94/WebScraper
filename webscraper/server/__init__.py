from functools import wraps
from flask import Flask
from flask_restful import Api, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///../../database.db"
app.config["JWT_SECRET_KEY"] = "super-oh-so-secret"
api = Api(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


@jwt.user_claims_loader
def add_admin_claim(identity):
    if "admin" in identity:
        return {"admin": True}
    else:
        return {"admin": False}


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if not claims["admin"]:
            abort(403, message="Unauthorized")
        else:
            return f(*args, **kwargs)

    return wrapper