import asyncio
from asyncio.tasks import Task
from itertools import product
from typing import List
from webscraper.models.website import Website
from webscraper.models.amazon import Amazon
import webscraper.errors as error
from webscraper.server import addToDatabase, db
from flask_restful import fields
from webscraper.models.user import UserModel
import datetime


class ProductModel(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.Integer, unique=True)
    url = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    history = db.relationship("PriceHistoryModel", backref="product", lazy=True)
    # seller = db.relationship("ProductBySellerModel", backref="product", lazy=True)
    # watch = db.relationship("ProductWatchModel", backref="product", lazy=True)

    resource_fields = {
        "id": fields.Integer,
        "upc": fields.Integer,
        "name": fields.String,
        # "watch": fields.List(fields.String(attribute="watch.id")),
    }

    def __eq__(self, other):
        if not (isinstance(self, other)):
            return False

        return self.id == other.id or self.url == other.url

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
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))

    resource_fields = {
        "id": fields.Integer,
        "user_id": fields.String,
        "product_id": fields.Integer,
    }


# class ProductBySellerModel(db.Model):
#     __tablename__ = "products_by_seller"

#     id = db.Column(db.Integer, db.ForeignKey("products.id"), primary_key=True)
#     seller_id = db.Column(db.Integer, db.ForeignKey("seller_info.id"), primary_key=True)
#     url_path = db.Column(db.String)
#     sku = db.Column(db.Integer)
#     current_price = db.Column(db.Float)

#     def __repr__(self) -> str:
#         return f"<ProductBySeller(id={self.id}, seller_id={self.seller_id}, url_path={self.url_path}, sku={self.sku}, current_price={self.current_price}>"


# class SellerInfoModel(db.Model):
#     __tablename__ = "seller_info"

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     base_url = db.Column(db.String)
#     products = db.relationship("ProductBySellerModel", backref="seller", lazy=True)


# Creates a scraper item based on url


# async def addProductsToDatabase(urls, user: UserModel):
#     if urls is None:
#         raise error.IncorrectInfoException

#     if not isinstance(urls, List):
#         urls = [urls]
#     tasks: List[Task] = []
#     sellers: List[SellerInfoModel] = []
#     products: List[Website] = []
#     for url in urls:
#         task = None
#         seller = None
#         if "bestbuy" in url:
#             task = asyncio.create_task(BestBuy.create(url))
#             seller = SellerInfoModel.query.filter_by(name="Best Buy").first()
#         elif "amazon" in url:
#             task = asyncio.create_task(Amazon.create(url))
#             seller = SellerInfoModel.query.filter_by(name="Amazon").first()
#         tasks.append(task)
#         sellers.append(seller)

#     # if len(tasks) == 0 or len(sellers) == 0:
#     #     raise error.InternalSeverException

#     [products.append(await task) for task in tasks]

#     productModels = []
#     [productModels.append(ProductModel(name=product.title)) for product in products]

#     # Only add products if it doesn't exist in database
#     productsToAdd = []
#     for i in range(len(productModels)):
#         if (
#             product := ProductModel.query.filter_by(name=productModels[i].name).first()
#         ) is not None:
#             productModels[i] = product
#         else:
#             productsToAdd.append(productModels[i])
#     addToDatabase(productsToAdd)

#     watches = []
#     [
#         watches.append(ProductWatchModel(user_id=user.id, product_id=product.id))
#         for product in productModels
#     ]

#     productSellers = []
#     [
#         productSellers.append(
#             ProductBySellerModel(
#                 id=productModels[i].id,
#                 seller_id=sellers[i].id,
#                 url_path=products[i].url_path,
#                 current_price=products[i].currentPrice,
#             )
#         )
#         for i in range(len(sellers))
#     ]

#     # Only add products if it doesn't exist in database
#     productSellersToAdd = []
#     for i in range(len(productSellers)):
#         if (
#             product := ProductBySellerModel.query.filter_by(
#                 id=productSellers[i].id, seller_id=productSellers[i].seller_id
#             )
#         ) is not None:
#             productSellers[i] = product
#         else:
#             productSellersToAdd.append(productSellers[i])

#     histories = []
#     [
#         histories.append(
#             PriceHistoryModel(
#                 id=productModels[i].id,
#                 date_added=datetime.datetime.utcnow(),
#                 price=products[i].currentPrice,
#             )
#         )
#         for i in range(len(productModels))
#     ]

#     addToDatabase(watches + productSellersToAdd + histories)


# def cleanDatabase():
#     """
#     Removes all product and its associated items if there is not watchlist for it.
#     """
#     products = ProductModel.query.all()
#     productsToDelete = []
#     for product in products:
#         if len(product.watch) == 0:
#             productsToDelete.append(product)

#     for product in productsToDelete:
#         id = product.id

#         [
#             db.session.delete(history)
#             for history in PriceHistoryModel.query.filter_by(id=id)
#         ]
#         [
#             db.sessiondelete(seller)
#             for seller in ProductBySellerModel.query.filter_by(id=id)
#         ]

#         db.session.commit()

#         db.session.delete(product)

#     db.session.commit()
