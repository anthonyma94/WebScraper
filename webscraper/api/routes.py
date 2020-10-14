from flask_restful import Resource
from flask import request
from webscraper.api import addProductToDatabase
import webscraper.utility.errors as error


class ProductApi(Resource):
    def get(self, product_id=None):
        if not product_id:
            view = {
                "id": None,
                "user_id": None,
                "product_id": None,
                "product_name": None,
                "current_price": None,
            }
            views = []

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
