from flask_restful import Resource, reqparse, abort, fields, marshal_with, marshal
from webscraper.server import db, app, api
from webscraper.server.database import UserModel
import uuid


db.create_all()

# test = UserModel(username="test", password="test")
# db.session.add(test)
# db.session.commit()


class User(Resource):
    @marshal_with(UserModel.resource_fields)
    def get(self, user_id=None):
        if user_id:
            result = UserModel.query.filter_by(id=user_id).first()
            if not result:
                abort(404, message="User cannot be found.")
        else:
            result = UserModel.query.all()
        return result

    def put(self, user_id=None):
        if user_id:
            abort(400, message="Cannot create user when user_id is provided.")

        args = reqparse.RequestParser()
        args.add_argument(
            "username", type=str, help="Please enter a username.", required=True
        )
        args.add_argument(
            "password", type=str, help="Please enter a password.", required=True
        )
        data = args.parse_args()
        user = UserModel(username=data["username"], password=data["password"])
        db.session.add(user)
        db.session.commit()
        return {"message": "User created."}, 201

    def delete(self, user_id=None):
        if not user_id:
            args = reqparse.RequestParser()
            args.add_argument(
                "confirm", type=str, help="Please confirm deletion.", required=True
            )
            data = args.parse_args()

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


api.add_resource(User, "/api/users", "/api/users/<string:user_id>")


# @app.route('/', methods=['GET'])
# def home():
#     return "<h1>Hello World</h1>"


if __name__ == "__main__":
    app.run(debug=True)
