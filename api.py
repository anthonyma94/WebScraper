from webscraper.models.bestbuy import BestBuy
from flask_restful import Resource, marshal_with
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from webscraper.api import (
    admin_required,
    app,
    api,
    loop,
    db,
    addProductToDatabase,
)
from webscraper.models.products import (
    ProductWatchModel,
    ProductModel,
    PriceHistoryModel,
)
import webscraper.utility.errors as error
import datetime

from webscraper.models.user import UserApi, UserModel, getUser


class LoginApi(Resource):
    def post(self):
        data = request.get_json()
        if "username" not in data or "password" not in data:
            raise error.MissingRequiredFieldException

        user: UserModel = UserModel.query.filter_by(username=data["username"]).first()
        authorized = user.check_password(data["password"])
        if not authorized:
            raise error.IncorrectInfoException
        else:
            access_token = create_access_token(
                identity=user.id,
                user_claims=["admin" if user.is_admin else None],
                expires_delta=datetime.timedelta(days=7),
            )
            return {"token": access_token}, 200


class WatchApi(Resource):
    @jwt_required
    @marshal_with(ProductWatchModel.resource_fields)
    def get(self, user_id=None):
        currentUser = getUser()
        if not user_id:
            if not currentUser.is_admin:
                raise error.InsufficientPermissionsException

            watch = ProductWatchModel.query.all()
            return watch, 200
        else:
            watch = ProductWatchModel.query.filter_by(user_id=user_id).all()
            return watch, 200


class ProductApi(Resource):
    @jwt_required
    def get(self, product_id=None):
        currentUser = getUser()
        if not product_id:
            view = {
                "id": None,
                "user_id": None,
                "product_id": None,
                "product_name": None,
                "current_price": None,
            }
            views = []

            watchlist = ProductWatchModel.query.filter_by(user_id=currentUser.id).all()

            # for i in watchlist:
            #     current_price = (
            #         ProductBySellerModel.query.filter_by(id=i.product_id)
            #         .first()
            #         .current_price
            #     )
            #     view = {}
            #     view["id"] = i.id
            #     view["user_id"] = i.user_id
            #     view["product_id"] = i.product_id
            #     view["product_name"] = i.product.name
            #     view["current_price"] = current_price
            #     views.append(view)

            return views, 200

    @jwt_required
    def post(self, product_id=None):
        if product_id:
            raise error.BadRequestException

        data = request.get_json()
        if "url" not in data:
            raise error.MissingRequiredFieldException("url required.")
        url = data["url"]
        if not (isinstance(url, str)):
            raise error.IncorrectInfoException("Invalid url.")

        currentUser = getUser()

        try:
            addProductToDatabase(currentUser, url=url)
        except error.InternalServerException as e:
            raise e

        # model = None
        # if "bestbuy" in url:
        #     model = BestBuy(url)

        # product = model.toDB()

        # # Check if product exists
        # products = ProductModel.query.all()
        # if product not in products:
        #     db.session.add(product)
        #     db.session.commit()
        # else:
        #     raise error.InternalServerException("Item already exists.")

        return {"message": "Product created."}, 201


api.add_resource(UserApi, "/api/users", "/api/users/<string:user_id>")
api.add_resource(LoginApi, "/api/login")
api.add_resource(ProductApi, "/api/products", "/api/products/<int:product_id>")
api.add_resource(
    WatchApi, "/api/products/watch", "/api/products/watch/<string:user_id>"
)


if __name__ == "__main__":
    app.run()
