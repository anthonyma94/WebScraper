from webscraper.server import db
from flask_restful import fields
import uuid


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    public_id = db.Column(
        db.String, nullable=False, default=str(uuid.uuid4()).replace("-", "")
    )

    resource_fields = {
        "id": fields.String(attribute="public_id"),
        "username": fields.String,
        "email": fields.String,
        "password": fields.String,
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


################################################


# import sqlalchemy as db
# from sqlalchemy import Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# engine = db.create_engine("sqlite:///database.db", echo=True)

# # Create database and table
# Base = declarative_base()

# Base.metadata.create_all(engine)


# class User(Base):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key=True)
#     email = Column(String, nullable=False)
#     username = Column(String, nullable=False)
#     password = Column(String, nullable=False)
#     public_id = Column(String, nullable=False)

#     def __repr__(self):
#         return f"<User(email='{self.email}', username='{self.username}'>"

# Session = sessionmaker(bind=engine)

# session = Session()

# user1 = User(email="test@123.com", username="test123")

# session.add(user1)
# session.commit()

# query = session.query(User).all()

# for row in query:
#     print(repr(row))
