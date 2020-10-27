from typing import List
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
from flask_restful import Resource
from flask import request
from webscraper.api import addProductToDatabase
import webscraper.utility.errors as error


class ProductApi(Resource):
    def get(self, product_id=None):
        if not product_id:
            models: List[ProductModel] = ProductModel.query.all()

            views = []

            for i in models:
                views.append({"id": i.id, "sku": i.sku, "url": i.url, "name": i.name})

            return views, 200

    def post(self, product_id=None):
        if product_id:
            raise error.BadRequestException

        data = request.get_json()
        if "url" not in data:
            raise error.MissingRequiredFieldException("url required.")
        url = data["url"]
        if not (isinstance(url, str)):
            raise error.IncorrectInfoException("Invalid url.")

        try:
            addProductToDatabase(url=url)
        except error.InternalServerException as e:
            raise e

        return {"message": "Product created."}, 201


class HistoryApi(Resource):
    def get(self, id=None):
        if not id:
            models = PriceHistoryModel.query.all()

            views = []

            for i in models:
                views.append(i.toDict())

            return views, 200
        else:
            model = PriceHistoryModel.query.get(id)

            return model.toDict(), 200


class ProfileApi(Resource):
    def get(self, id=None):
        if not id:
            models: List[ProfileModel] = ProfileModel.query.all()
        else:
            models = [ProfileModel.query.get(id)]

        views = []

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

        model = profile.toDB()

        db.session.add(model)
        db.session.commit()

        return {"message": "Profile created"}, 200
