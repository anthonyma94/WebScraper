import flask
import os
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config["DEBUG"] = True
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # public_id = db.Column(db.String(100), unique=True, nullable=False)
    products_watch = db.relationship(
        "ProductsWatch", backref="user", lazy=True)

    def __repr__(self):
        return f"<User(username='{self.username}')>"


class ProductsWatch(db.Model):
    __tablename__ = "products_watch"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey(
        "users.id"), nullable=False)

    def __repr__(self):
        return f"<ProductsWatch(user_id='{self.user_id}'>"


@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello World</h1>"


if __name__ == "__main__":
    app.run()
