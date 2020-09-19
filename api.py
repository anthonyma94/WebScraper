from flask_restful import Resource, reqparse, abort, fields, marshal_with
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from webscraper.server import admin_required, db, app, api
from webscraper.server.database import UserModel
import datetime


class UserApi(Resource):
    @marshal_with(UserModel.resource_fields)
    @jwt_required
    @admin_required
    def get(self, user_id=None):
        if user_id:
            result = UserModel.query.filter_by(id=user_id).first()
            if not result:
                abort(404, message="User cannot be found.")
        else:
            result = UserModel.query.all()
        return result

    def post(self, user_id=None):
        if user_id:
            abort(400, message="Cannot create user when user_id is provided.")

        data = request.get_json()
        user = UserModel(
            username=data["username"], password=data["password"], email=data["email"]
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "User created."}, 201

    @jwt_required
    def delete(self, user_id=None):
        if not user_id:
            data = request.get_json()

            if data["confirm"] == "yes":
                users = UserModel.query.all()
                for user in users:
                    db.session.delete(user)
                db.session.commit()
                return {"message": "All users deleted."}, 200
            else:
                abort(400, message="Cannot perform deletion.")
        else:
            user = UserModel.query.filter_by(public_id=user_id).first()
            if not user:
                abort(404, message="User cannot be found.")
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted"}, 200


class LoginApi(Resource):
    def post(self):
        body = request.get_json()
        user: UserModel = UserModel.query.filter_by(username=body["username"]).first()
        authorized = user.check_password(body["password"])
        if not authorized:
            abort(401, message="Invalid email or password.")
        else:
            expires = datetime.timedelta(days=7)
            identity = user.public_id
            if user.is_admin:
                identity += "admin"
            access_token = create_access_token(identity=identity, expires_delta=expires)
            return {"token": access_token}, 200


api.add_resource(UserApi, "/api/users", "/api/users/<string:user_id>")
api.add_resource(LoginApi, "/api/login")


if __name__ == "__main__":
    app.run(debug=True)
