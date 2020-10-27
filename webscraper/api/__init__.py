# from functools import wraps
from webscraper.models.profiles import Address, CreditCard, ShoppingProfile
from webscraper.models.cc import CanadaComputers
import webscraper.utility.errors as error

# from webscraper.models.user import UserModel
from webscraper.models.bestbuy import BestBuy
from webscraper.models.products import (
    ProductModel,
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
app._static_folder = "../public/static"
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
        else:
            raise error.IncorrectInfoException

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

        profile = ShoppingProfile(
            email="anthonyma940603@gmail.com",
            actEmail="anthonyma940603@gmail.com",
            actPassword="8290F9AF",
            shippingAddress=Address(
                address="3692 Water St",
                city="Kitchener",
                firstName="Test",
                lastName="Test",
                phoneNumber="2894439715",
                province="ON",
                postalCode="N2H5A5",
            ),
            creditCard=CreditCard(
                firstName="Test",
                lastName="Test",
                creditCardNumber="4263982640269299",
                cvv="837",
                expMonth="2",
                expYear="2023",
                type="VISA",
                billingAddress=Address(
                    address="3692 Water St",
                    city="Kitchener",
                    firstName="Test",
                    lastName="Test",
                    phoneNumber="2894439715",
                    province="ON",
                    postalCode="N2H5A5",
                ),
            ),
        )

        model = profile.toDB()

        try:
            db.session.add(model)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            db.session.flush()

        addProductToDatabase(
            url="https://www.bestbuy.ca/en-ca/product/acer-spin-11-6-touchscreen-2-in-1-chromebook-silver-mediatek-m8183-64gb-ssd-4gb-ram-chrome-os/14742355"
        )
