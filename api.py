from webscraper.models.bestbuy import BestBuy
from flask_restful import Resource, marshal_with
from flask import request

from webscraper.api import (
    app,
    api,
    loop,
    db,
    addProductToDatabase,
)
from webscraper.models.products import (
    ProductModel,
    PriceHistoryModel,
)
import webscraper.utility.errors as error
import datetime


class ProductApi(Resource):
    def get(self, product_id=None):
        # currentUser = getUser()
        if not product_id:
            view = {
                "id": None,
                "user_id": None,
                "product_id": None,
                "product_name": None,
                "current_price": None,
            }
            views = []

            # watchlist = ProductWatchModel.query.filter_by(user_id=currentUser.id).all()

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


api.add_resource(ProductApi, "/api/products", "/api/products/<int:product_id>")


if __name__ == "__main__":
    app.run()
