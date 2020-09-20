from webscraper.server import db
from flask_restful import fields
from webscraper.models.user import UserModel
import datetime


class ProductModel(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    upc = db.Column(db.Integer, unique=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.LargeBinary)
    history = db.relationship("PriceHistoryModel", backref="product", lazy=True)
    seller = db.relationship("ProductBySellerModel", backref="product", lazy=True)
    watch = db.relationship("ProductWatchModel", backref="product", lazy=True)

    resource_fields = {
        "id": fields.Integer,
        "upc": fields.Integer,
        "name": fields.String,
        "watch": fields.List(fields.String(attribute="watch.id")),
    }

    def __repr__(self) -> str:
        return f"<Product(name='{self.name}', id='{self.id}', upc='{self.upc}')>"


class PriceHistoryModel(db.Model):
    __tablename__ = "price_history"

    id = db.Column(db.Integer, db.ForeignKey("products.id"), primary_key=True)
    date_added = db.Column(
        db.DateTime, primary_key=True, default=datetime.datetime.utcnow
    )
    price = db.Column(db.Float)


class ProductWatchModel(db.Model):
    __tablename__ = "products_watch"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("users.public_id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))

    resource_fields = {
        "id": fields.Integer,
        "user_id": fields.String,
        "product_id": fields.Integer,
        "product": fields.String(attribute="product.name"),
        "current_price": fields.Float(attribute="product.seller[0].current_price"),
    }


class ProductBySellerModel(db.Model):
    __tablename__ = "products_by_seller"

    id = db.Column(db.Integer, db.ForeignKey("products.id"), primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("seller_info.id"), primary_key=True)
    url_path = db.Column(db.String)
    sku = db.Column(db.Integer)
    current_price = db.Column(db.Float)

    def __repr__(self) -> str:
        return f"<ProductBySeller(id={self.id}, seller_id={self.seller_id}, url_path={self.url_path}, sku={self.sku}, current_price={self.current_price}>"


class SellerInfoModel(db.Model):
    __tablename__ = "seller_info"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    base_url = db.Column(db.String)
    products = db.relationship("ProductBySellerModel", backref="seller", lazy=True)
