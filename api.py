from flask_restful import Resource, abort, fields, marshal_with
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from webscraper.server import admin_required, db, app, api, loop, addToDatabase
from webscraper.server.database import (
    # UserModel,
    ProductWatchModel,
    ProductModel,
    PriceHistoryModel,
    ProductBySellerModel,
    SellerInfoModel,
)
from webscraper.models.amazon import Amazon
from webscraper.models.bestbuy import BestBuy
import datetime

from webscraper.models.user import UserApi, UserModel, getUser


class LoginApi(Resource):
    def post(self):
        data = request.get_json()
        user: UserModel = UserModel.query.filter_by(username=data["username"]).first()
        authorized = user.check_password(data["password"])
        if not authorized:
            abort(401, message="Invalid email or password.")
        else:
            expires = datetime.timedelta(days=7)
            identity = user.public_id
            user_claims = []
            if user.is_admin:
                user_claims.append("admin")
            access_token = create_access_token(
                identity=identity, user_claims=user_claims, expires_delta=expires
            )
            return {"token": access_token}, 200


class ProductApi(Resource):
    @jwt_required
    @marshal_with(ProductWatchModel.resource_fields)
    def get(self, product_id=None):
        currentUser = getUser()
        if not product_id:

            watchlist = ProductWatchModel.query.filter_by(
                user_id=currentUser.public_id
            ).all()
            #     # productList = []
            #     # for i in watchlist:
            #     #     productList.append(
            #     #         ProductModel.query.filter_by(id=i.product_id).first()
            #     #     )
            # return {"User": len(watchlist)}, 200

            return watchlist, 200


#     @jwt_required
#     def post(self, product_id=None):
#         if product_id:
#             abort(400, "Product id given.")

#         data = request.get_json()
#         url = data["url"]

#         product = None
#         seller = None
#         user = getUser()

#         if "bestbuy" in url:
#             product = loop.run_until_complete(BestBuy.create(url))
#             seller = SellerInfoModel.query.filter_by(name="Best Buy").first()
#         elif "amazon" in url:
#             product = loop.run_until_complete(Amazon.create(url))
#             seller = SellerInfoModel.query.filter_by(name="Amazon").first()

#         productModel = ProductModel(name=product.title)

#         addToDatabase(productModel)

#         productWatch = ProductWatchModel(
#             user_id=user.public_id, product_id=productModel.id
#         )

#         productSeller = ProductBySellerModel(
#             id=productModel.id,
#             seller_id=seller.id,
#             url_path=product.url_path,
#             current_price=product.currentPrice,
#         )

#         addToDatabase([productSeller, productWatch])

#         return {"message": "Product created."}, 201


api.add_resource(UserApi, "/api/users", "/api/users/<string:user_id>")
api.add_resource(LoginApi, "/api/login")
api.add_resource(ProductApi, "/api/products", "/api/products/<int:product_id>")


if __name__ == "__main__":
    app.run(debug=True)
