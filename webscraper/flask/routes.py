import datetime
from typing import List
from webscraper.models.tasks import TaskModel
from webscraper.models.bestbuy import BestBuy
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
from webscraper.models.products import ProductModel
from webscraper.utility.utils import (
    db,
    delete_from_database,
    get_from_database,
    update_database,
)
import webscraper.utility.errors as error
from flask_restful import Resource, marshal_with
from flask import request
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
            if "bestbuy" in url:
                item = BestBuy(url).toDB().add_to_database(silent=False)
            elif "canadacomputers" in url:
                item = CanadaComputers(url).toDB().add_to_database(silent=False)
            else:
                raise error.InternalServerException
        except IntegrityError:
            raise error.AlreadyExistsException("Product already exists.")
        except Exception as e:
            # TODO: Fix all related exceptions
            raise error.InternalServerException(f"Almost made it.\n {e}")

        return item, 201


class TaskApi(Resource):
    def get(self, id=None):
        if not id:
            items = get_from_database(TaskModel)
        else:
            items = get_from_database(TaskModel, id=int(id))

        return list(map(lambda x: x.toDict(), items)), 200

    def post(self):
        data = request.get_json()
        if not data:
            raise error.InternalServerException

        if "url" not in data or data["url"] == "":
            raise error.InternalServerException

        url = data["url"]

        if "bestbuy" in url:
            item = BestBuy(url)
        elif "canadacomputers" in url:
            item = CanadaComputers(url)
        else:
            raise error.InternalServerException

        product = item.toDB().add_to_database()

        taskItem = TaskModel(
            product=product.id,
            price_limit=data["price_limit"],
            notify_on_available=data["notify_on_available"],
            purchase=data["purchase"],
            profile=data["profile"] if data["purchase"] else None,
        )

        try:
            taskItem.add_to_database(silent=False)
        except IntegrityError:
            raise error.AlreadyExistsException

        return {"message": "Task added."}, 200

    def delete(self, id):
        if not id or id == "":
            raise error.InternalServerException

        try:
            delete_from_database(TaskModel, int(id), silent=False)
        except Exception:
            raise error.InternalServerException

        return {"message": "Task deleted."}, 200


# class HistoryApi(Resource):
#     @marshal_with(PriceHistoryModel.resource_fields)
#     def get(self, id=None):
#         start = request.args.get("start")
#         end = request.args.get("end")

#         if bool(start) != bool(end):
#             raise error.MissingRequiredFieldException(
#                 "Missing start or end parameters."
#             )

#         if start and end:
#             try:
#                 start = datetime.datetime.utcfromtimestamp(float(start))
#                 end = datetime.datetime.utcfromtimestamp(float(end))
#             except:
#                 raise error.IncorrectInfoException("Invalid start or end parameters.")

#         if id:
#             models = (
#                 PriceHistoryModel.query.filter_by(id=id).all()
#                 if not start and not end
#                 else PriceHistoryModel.query.filter(
#                     and_(
#                         PriceHistoryModel.id == id,
#                         between(PriceHistoryModel.created_on, start, end),
#                     )
#                 ).all()
#             )
#         else:
#             models = (
#                 PriceHistoryModel.query.all()
#                 if not start and not end
#                 else PriceHistoryModel.query.filter(
#                     between(PriceHistoryModel.created_on, start, end)
#                 ).all()
#             )

#         if not models or len(models) == 0:
#             raise error.NotFoundException("Cannot find history.")

#         return models, 200

#     @marshal_with(PriceHistoryModel.resource_fields)
#     def post(self, id=None):
#         if not id:
#             raise error.MissingRequiredFieldException("Missing ID.")

#         model = ProductModel.query.get(id)
#         if not model:
#             raise error.NotFoundException("Cannot find product.")

#         if "bestbuy" in model.url:
#             product = BestBuy.fromDB(model)
#         elif "canadacomputers" in model.url:
#             product = CanadaComputers.fromDB(model)
#         else:
#             product = None

#         history = PriceHistoryModel(
#             id=id, price=product.currentPrice, is_available=product.isAvailable
#         ).add_to_database()

#         return history, 200


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
            raise error.InternalServerException("Could not parse JSON.")

        card = None
        shipping = None

        try:
            card_dict = data["credit_card"]

            billing_dict = card_dict["billing_address"]
            billing = Address(
                id=billing_dict["id"]
                if "id" in billing_dict and billing_dict["id"] != ""
                else None,
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

            try:
                if billing.id and billing.id != "":
                    billing = Address.fromDB(
                        update_database(
                            get_from_database(AddressModel, id=billing.id),
                            billing.toDB(),
                        )
                    )
            except AttributeError:
                pass

            card = CreditCard(
                id=card_dict["id"]
                if "id" in card_dict and card_dict["id"] != ""
                else None,
                firstName=card_dict["first_name"],
                lastName=card_dict["last_name"],
                creditCardNumber=card_dict["card_number"],
                cvv=card_dict["cvv"],
                expMonth=card_dict["exp_month"],
                expYear=card_dict["exp_year"],
                type=card_dict["type"].upper(),
                billingAddress=billing,
            )

            try:
                if card.id and card.id != "":
                    card = CreditCard.fromDB(
                        update_database(
                            get_from_database(CreditCardModel, id=card.id), card.toDB()
                        )
                    )
            except AttributeError:
                pass

            shipping_dict = data["shipping_address"]

            shipping = Address(
                id=shipping_dict["id"]
                if "id" in shipping_dict and shipping_dict != ""
                else None,
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

            try:
                if shipping.id and shipping.id != "":
                    shipping = Address.fromDB(
                        update_database(
                            get_from_database(AddressModel, id=shipping.id),
                            shipping.toDB(),
                        )
                    )
            except AttributeError:
                pass
        except KeyError as e:
            raise error.IncorrectInfoException(f"Missing {e} from data.")

        profile = ShoppingProfile(
            id=data["id"] if "id" in data else None,
            email=data["email"],
            actEmail=data["account"]["username"]
            if "account" in data and data["account"]["username"] != ""
            else None,
            actPassword=data["account"]["password"]
            if "account" in data and data["account"]["password"] != ""
            else None,
            shippingAddress=shipping,
            creditCard=card,
        )
        try:
            if profile.id and profile.id != "":
                model = update_database(
                    get_from_database(ProfileModel, id=profile.id), profile.toDB()
                )
            else:
                model = profile.toDB().add_to_database(silent=False)
        except AttributeError:
            model = profile.toDB().add_to_database(silent=False)

        return model.toDict(), 200


bp = Blueprint(
    "public",
    __name__,
    template_folder="../public/templates",
)


@bp.route("/")
@bp.route("/index.html")
def index():
    profiles, response = ProfileApi.get(None)
    tasks, response = TaskApi.get(None)
    return render_template("index.html", profiles=profiles, tasks=tasks)


@bp.route("/profile")
@bp.route("/profile.html")
def profile():
    return render_template("profile.html")


@bp.route("/profiles")
@bp.route("/profiles.html")
def profiles():
    views = []
    models: List[ProfileModel] = ProfileModel.query.all()
    [views.append(i.toDict()) for i in models]
    return render_template("profiles.html", models=views)
