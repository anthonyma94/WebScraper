from flask_bcrypt import check_password_hash, generate_password_hash
from flask_jwt_extended.utils import get_jwt_identity
from flask_restful import Resource, marshal_with, fields
from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from webscraper.utility.config import db, ROLES
import datetime, uuid
import webscraper.utility.errors as error


class UserModel(db.Model):
    """Model class for user table in database

    Args:
        db (flask_sqlalchemy.Model): Flask SQLAlchemy Model object
    """

    __tablename__ = "users"

    id = db.Column(
        db.String, primary_key=True, default=str(uuid.uuid4()).replace("-", "")
    )
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, default=ROLES.watch.value)
    date_created = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    watch = db.relationship("ProductWatchModel", backref="user", lazy=True)

    def __init__(self, **kwargs):
        super(UserModel, self).__init__(**kwargs)

        if not self.verify_password():
            raise ValueError

        self.password = generate_password_hash(self.password).decode("utf-8")

    @property
    def is_admin(self) -> bool:
        return self.role == ROLES.admin.value

    @property
    def user_role(self) -> str:
        if self.role not in ROLES:
            return ROLES.watch.name
        return ROLES(self.role).name

    def verify_password(self) -> bool:
        """Verifies the strength of the given password.
        Password needs to be at least 8 characters, 1 number, 1 upper-case, 1 lower-case.
        To check hased passwords use check_password().

        Returns:
            bool: Whether the password passes.
        """
        lower = upper = digit = 0

        if len(self.password) < 8:
            return False
        for i in self.password:
            upper += 1 if i.isupper() else 0
            lower += 1 if i.islower() else 0
            digit += 1 if i.isdigit() else 0
        if upper == 0 or lower == 0 or digit == 0:
            return False
        return True

    def check_password(self, password) -> bool:
        """Checks given password against hashed password

        Args:
            password (str): password given by user

        Returns:
            bool: whether password is valid
        """
        return check_password_hash(self.password, password)

    # Resource fields is needed for object mapping for Flask
    resource_fields = {
        "id": fields.String,
        "username": fields.String,
        "email": fields.String,
        "password": fields.String,
        "date_created": fields.DateTime,
        "is_admin": fields.Boolean,
    }

    def __repr__(self):
        return (
            f"<User(id='{self.id}', email='{self.email}', username='{self.username}')>"
        )


class UserApi(Resource):
    """API used in Flask

    Args:
        Resource (flask_restful.Resource): Flask RESTful Resource obj
    """

    @marshal_with(UserModel.resource_fields)  # Used for object mapping for Flask
    @jwt_required
    def get(self, user_id=None):
        currentUser = getUser()
        if user_id:
            result = UserModel.query.filter_by(id=user_id).first()
            if not result:
                raise error.UserNotFoundException
            if currentUser.id != result.id and not currentUser.is_admin:
                raise error.InsufficientPermissionsException
        else:
            result = UserModel.query.all()
        return result

    def post(self, user_id=None):
        if user_id:
            raise error.BadRequestException(
                description="Cannot create user when user_id is provided."
            )

        data = request.get_json()

        if "username" not in data or "password" not in data or "email" not in data:
            raise error.MissingRequiredFieldException
        try:
            user = UserModel(
                username=data["username"],
                password=data["password"],
                email=data["email"],
            )
        except ValueError:
            raise error.ValueError(description="Password requirements not met.")
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            db.session.flush()
            raise error.AlreadyExistsException(
                description="Username already exists in database."
            )
        return {"message": "User created."}, 201

    @jwt_required
    def delete(self, user_id=None):
        currentUser = getUser()
        if not user_id:
            data = request.get_json()

            if not currentUser.is_admin:
                raise error.InsufficientPermissionsException

            if "confirm" not in data or data["confirm"] != "yes":
                raise error.BadRequestException

            users = UserModel.query.all()
            for user in users:
                db.session.delete(user)
            db.session.commit()
            return {"message": "All users deleted."}, 200
        else:
            userToDelete = UserModel.query.filter_by(id=user_id).first()
            if not userToDelete:
                raise error.UserNotFoundException
            if currentUser.id != userToDelete.id and not currentUser.is_admin:
                raise error.InsufficientPermissionsException

            db.session.delete(userToDelete)
            db.session.commit()
            return {"message": "User deleted"}, 200


def getUser() -> UserModel:
    user_id = get_jwt_identity()
    user = UserModel.query.filter_by(id=user_id).first()

    if not user:
        raise error.UserNotFoundException

    return user