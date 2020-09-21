import asyncio
from typing import Tuple
from flask_restful import Resource, marshal_with
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from webscraper.server import admin_required, app, api, loop, addToDatabase
from webscraper.server.database import (
    ProductWatchModel,
    ProductModel,
    PriceHistoryModel,
    ProductBySellerModel,
    SellerInfoModel,
    addProductsToDatabase,
)
import webscraper.server.errors as error
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
                identity=user.public_id,
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

            watchlist = ProductWatchModel.query.filter_by(
                user_id=currentUser.public_id
            ).all()

            for i in watchlist:
                current_price = (
                    ProductBySellerModel.query.filter_by(id=i.product_id)
                    .first()
                    .current_price
                )
                view = {}
                view["id"] = i.id
                view["user_id"] = i.user_id
                view["product_id"] = i.product_id
                view["product_name"] = i.product.name
                view["current_price"] = current_price
                views.append(view)

            return views, 200

    @jwt_required
    def post(self, product_id=None):
        if product_id:
            raise error.BadRequestException

        data = request.get_json()
        if "url" not in data:
            raise error.MissingRequiredFieldException("url required.")
        url = data["url"]
        currentUser = getUser()

        loop.run_until_complete(addProductsToDatabase(url, currentUser))

        return {"message": "Product created."}, 201


api.add_resource(UserApi, "/api/users", "/api/users/<string:user_id>")
api.add_resource(LoginApi, "/api/login")
api.add_resource(ProductApi, "/api/products", "/api/products/<int:product_id>")
api.add_resource(
    WatchApi, "/api/products/watch", "/api/products/watch/<string:user_id>"
)


if __name__ == "__main__":
    app.run(debug=True)
