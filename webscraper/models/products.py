from webscraper.utility.config import db, add_to_database
from sqlalchemy import and_
from flask_restful import fields, marshal
import datetime


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
        "sku": fields.Integer,
        "name": fields.String,
        "image_url": fields.String,
    }

    def __eq__(self, other):
        if not (isinstance(other, ProductModel)):
            return False

        return self.id == other.id or self.url == other.url

    def __repr__(self):
        return marshal(self, self.resource_fields)

    def add_to_database(self, **kwargs):
        return add_to_database(
            self, ProductModel.query.filter_by(url=self.url).first(), **kwargs
        )


class PriceHistoryModel(db.Model):
    __tablename__ = "price_history"

    id = db.Column(db.Integer, db.ForeignKey("products.id"), primary_key=True)
    created_on = db.Column(
        db.DateTime,
        primary_key=True,
        default=lambda _: datetime.datetime.utcnow().replace(microsecond=0),
    )
    price = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, nullable=False)

    resource_fields = {
        "id": fields.Integer,
        "created_on": fields.DateTime,
        "price": fields.Float,
        "is_available": fields.Boolean,
    }

    def add_to_database(self, **kwargs):
        return add_to_database(
            self,
            PriceHistoryModel.query.filter(
                and_(
                    PriceHistoryModel.id == self.id,
                    PriceHistoryModel.created_on == self.created_on,
                )
            ).first(),
            **kwargs,
        )

    def __repr__(self):
        return marshal(self, self.resource_fields)
