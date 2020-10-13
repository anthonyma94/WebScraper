from webscraper.utility.config import db
from flask_restful import fields
import datetime
from sqlalchemy.exc import IntegrityError


class ProductModel(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.Integer, unique=True)
    url = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    history = db.relationship("PriceHistoryModel", backref="product", lazy=True)

    resource_fields = {
        "id": fields.Integer,
        "upc": fields.Integer,
        "name": fields.String,
    }

    def __eq__(self, other):
        if not (isinstance(other, ProductModel)):
            return False

        return self.id == other.id or self.url == other.url

    def __repr__(self) -> str:
        return f"<Product(name='{self.name}', id='{self.id}', upc='{self.upc}')>"

    def add_to_database(self):
        item = self
        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            db.session.flush()
            item = ProductModel.query.filter_by(url=self.url).first()
        return item


class PriceHistoryModel(db.Model):
    __tablename__ = "price_history"

    id = db.Column(db.Integer, db.ForeignKey("products.id"), primary_key=True)
    date_added = db.Column(
        db.DateTime, primary_key=True, default=datetime.datetime.utcnow
    )
    price = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, nullable=False)