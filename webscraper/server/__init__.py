from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///../../database.db"
api = Api(app)
db = SQLAlchemy(app)