# from functools import wraps
from webscraper.models.cc import CanadaComputers
import webscraper.utility.errors as error

# from webscraper.models.user import UserModel
from webscraper.models.bestbuy import BestBuy
from webscraper.models.products import (
    ProductModel,
    # ProductWatchModel,
    PriceHistoryModel,
)
from flask import Flask
from flask_restful import Api, abort
from webscraper.utility.config import db

# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims
from dotenv import load_dotenv, find_dotenv
import asyncio
from sqlalchemy.exc import IntegrityError

if find_dotenv() != "":
    load_dotenv(find_dotenv())


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///../../database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
api = Api(app)
loop = asyncio.get_event_loop()


def addProductToDatabase(url=None, item: ProductModel = None) -> bool:
    if (url is None and item is None) or (url is not None and item is not None):
        raise error.IncorrectInfoException

    item = None
    if url is not None:
        if "bestbuy" in url:
            item = BestBuy(url).toDB()
        elif "canadacomputers" in url:
            item = CanadaComputers(url).toDB()

    try:
        db.session.add(item)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        db.session.flush()
        item = ProductModel.query.filter_by(url=item.url).first()

    product = None
    if "bestbuy" in item.url:
        product = BestBuy.fromDB(item)
    elif "canadacomputers" in item.url:
        product = CanadaComputers.fromDB(item)

    history = PriceHistoryModel(
        id=item.id,
        price=product.currentPrice,
        is_available=product.isAvailable,
    )
    db.session.add(history)
    db.session.commit()


with app.app_context():
    db.init_app(app)
    engine = db.get_engine()
    if not (ProductModel.metadata.tables[ProductModel.__tablename__].exists(engine)):
        db.create_all()

    if app.config["ENV"].lower() == "development":

        # try:
        addProductToDatabase(
            url="https://www.bestbuy.ca/en-ca/product/acer-spin-11-6-touchscreen-2-in-1-chromebook-silver-mediatek-m8183-64gb-ssd-4gb-ram-chrome-os/14742355"
        )
        # except:
        #     pass
