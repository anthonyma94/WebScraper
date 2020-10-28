import datetime
from typing import List
from webscraper.models.bestbuy import BestBuy
from webscraper.models.amazon import Amazon
from webscraper.models.cc import CanadaComputers
from sqlalchemy import between, and_
from sqlalchemy.exc import IntegrityError
from webscraper.models.profiles import (
    Address,
    AddressModel,
    CreditCard,
    CreditCardModel,
    ProfileModel,
    ShoppingProfile,
)
from webscraper.models.products import PriceHistoryModel, ProductModel
from webscraper.utility.config import db
import webscraper.utility.errors as error
from flask_restful import Resource, marshal, marshal_with
from flask import request
from webscraper.flask import addProductToDatabase
from flask.blueprints import Blueprint
from flask.templating import render_template


class ProductApi(Resource):
    @marshal_with(ProductModel.resource_fields)
    def get(self, product_id=None):
        models = (
            ProductModel.query.all()
            if not product_id
            else ProductModel.query.get(product_id)
        )

        if not models or len(models) == 0:
            raise error.NotFoundException("Cannot find product(s).")

        return models, 200

    @marshal_with(ProductModel.resource_fields)
    def post(self, product_id=None):
        if product_id:
            raise error.BadRequestException

        try:
            data = request.get_json()
        except:
            raise error.InternalServerException("Could not resolve JSON.")

        if "url" not in data:
            raise error.MissingRequiredFieldException("url required.")
        url = data["url"]
        if not (isinstance(url, str)):
            raise error.IncorrectInfoException("Invalid url.")

        result = ProductModel.query.filter_by(url=url).first()
        if result:
            raise error.AlreadyExistsException

        try:
            item = addProductToDatabase(url=url, silent=False)
        except IntegrityError:
            raise error.AlreadyExistsException("Product already exists.")
        except Exception as e:
            # TODO: Fix all related exceptions
            raise error.InternalServerException(f"Almost made it.\n {e}")

        return item, 201


class HistoryApi(Resource):
    @marshal_with(PriceHistoryModel.resource_fields)
    def get(self, id=None):
        start = request.args.get("start")
        end = request.args.get("end")

        if bool(start) != bool(end):
            raise error.MissingRequiredFieldException(
                "Missing start or end parameters."
            )

        if start and end:
            try:
                start = datetime.datetime.utcfromtimestamp(float(start))
                end = datetime.datetime.utcfromtimestamp(float(end))
            except:
                raise error.IncorrectInfoException("Invalid start or end parameters.")

        if id:
            models = (
                PriceHistoryModel.query.filter_by(id=id).all()
                if not start and not end
                else PriceHistoryModel.query.filter(
                    and_(
                        PriceHistoryModel.id == id,
                        between(PriceHistoryModel.created_on, start, end),
                    )
                ).all()
            )
        else:
            models = (
                PriceHistoryModel.query.all()
                if not start and not end
                else PriceHistoryModel.query.filter(
                    between(PriceHistoryModel.created_on, start, end)
                ).all()
            )

        if not models or len(models) == 0:
            raise error.NotFoundException("Cannot find history.")

        return models, 200

    @marshal_with(PriceHistoryModel.resource_fields)
    def post(self, id=None):
        if not id:
            raise error.MissingRequiredFieldException("Missing ID.")

        model = ProductModel.query.get(id)
        if not model:
            raise error.NotFoundException("Cannot find product.")

        if "bestbuy" in model.url:
            product = BestBuy.fromDB(model)
        elif "canadacomputers" in model.url:
            product = CanadaComputers.fromDB(model)
        else:
            product = None

        history = PriceHistoryModel(
            id=id, price=product.currentPrice, is_available=product.isAvailable
        ).add_to_database()

        return history, 200


class ProfileApi(Resource):
    def get(self, id=None):
        if not id:
            models: List[ProfileModel] = ProfileModel.query.all()
        else:
            models = [ProfileModel.query.get(id)]

        views = []

        if len(models) == 0:
            raise error.NotFoundException("ID cannot be found.")

        try:
            for i in models:
                views.append(i.toDict())
        except Exception:
            raise error.InternalServerException

        return views, 200

    def post(self):
        data = request.get_json()
        if not data:
            raise error.MissingRequiredFieldException

        card = None
        shipping = None
        if "credit_card" in data:
            card_dict = data["credit_card"]

            if not (isinstance(card_dict, int)):
                billing = None
                billing_dict = card_dict["billing_address"]
                if not (isinstance(billing_dict, int)):
                    billing = Address(
                        address=billing_dict["address"],
                        city=billing_dict["city"],
                        firstName=billing_dict["first_name"],
                        lastName=billing_dict["last_name"],
                        phoneNumber=billing_dict["phone_number"],
                        postalCode=billing_dict["postal_code"],
                        province=billing_dict["province"],
                        apartmentNumber=billing_dict["apartment_number"],
                        extension=billing_dict["extension"],
                    )
                else:
                    billing = Address.fromDB(AddressModel.query.get(billing_dict))
                card = CreditCard(
                    firstName=card_dict["first_name"],
                    lastName=card_dict["last_name"],
                    creditCardNumber=card_dict["number"],
                    cvv=card_dict["cvv"],
                    expMonth=card_dict["exp_month"],
                    expYear=card_dict["exp_year"],
                    type=card_dict["type"].upper(),
                    billingAddress=billing,
                )
            else:
                card = CreditCard.fromDB(CreditCardModel.query.get(card_dict))

        shipping_dict = data["shipping_address"]

        if not (isinstance(shipping_dict, int)):
            shipping = Address(
                address=shipping_dict["address"],
                city=shipping_dict["city"],
                firstName=shipping_dict["first_name"],
                lastName=shipping_dict["last_name"],
                phoneNumber=shipping_dict["phone_number"],
                postalCode=shipping_dict["postal_code"],
                province=shipping_dict["province"],
                apartmentNumber=shipping_dict["apartment_number"],
                extension=shipping_dict["extension"],
            )
        else:
            shipping = Address.fromDB(AddressModel.query.get(shipping_dict))

        profile = ShoppingProfile(
            email=data["email"],
            shippingAddress=shipping,
            creditCard=card,
        )

        try:
            model = profile.toDB().add_to_database(silent=False)
        except IntegrityError:
            raise error.AlreadyExistsException("Profile already exists.")

        return {"message": "Profile created"}, 200


bp = Blueprint(
    "public",
    __name__,
    template_folder="../public/templates",
)


@bp.route("/")
@bp.route("/index.html")
def index():
    return render_template("index.html")


@bp.route("/profile")
@bp.route("/profile.html")
def profile():
    return render_template("profile.html")