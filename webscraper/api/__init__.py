from functools import wraps
from webscraper.models.cc import CanadaComputers
import webscraper.utility.errors as error
from webscraper.models.user import UserModel
from webscraper.models.bestbuy import BestBuy
from webscraper.models.products import (
    ProductModel,
    ProductWatchModel,
    PriceHistoryModel,
)
from flask import Flask
from flask_restful import Api, abort
from webscraper.utility.config import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims
from dotenv import load_dotenv, find_dotenv
import asyncio
from sqlalchemy.exc import IntegrityError

if find_dotenv() != "":
    load_dotenv(find_dotenv())


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///../../database.db"
app.config["JWT_SECRET_KEY"] = "super-oh-so-secret"
app.config["JWT_ERROR_MESSAGE_KEY"] = "message"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
loop = asyncio.get_event_loop()


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if "admin" not in claims:
            abort(403, message="Unauthorized")
        else:
            return f(*args, **kwargs)

    return wrapper


def addProductToDatabase(user: UserModel, url=None, item: ProductModel = None) -> bool:
    if (url is None and item is None) or (url is not None and item is not None):
        raise error.IncorrectInfoException

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

    watch = ProductWatchModel(user_id=user.id, product_id=item.id)
    try:
        db.session.add(watch)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        db.session.flush()
        raise error.InternalServerException("Product watch already exists for user.")

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
        admin = UserModel(
            email="admin@admin.com",
            password="Password1",
            first_name="admin",
            last_name="admin",
            id="admin",
            role="admin",
        )
        try:
            db.session.add(admin)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            db.session.flush()
            admin = UserModel.query.filter_by(email="admin@admin.com").first()

        try:
            addProductToDatabase(
                admin,
                url="https://www.bestbuy.ca/en-ca/product/acer-spin-11-6-touchscreen-2-in-1-chromebook-silver-mediatek-m8183-64gb-ssd-4gb-ram-chrome-os/14742355",
            )
        except:
            pass
