from flask import request
from flask_restx import Namespace, Resource
from models.user import User
from util import util

api = Namespace('users')


@api.route('/')
class Users(Resource):
    def get(self):
        users = User.objects.values()
        data = [util.parse_mongo_to_jsonable(user) for user in users]
        return {'data': data}

    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        name = data['name']
        email = data['email']
        phone = data['phone']
        created_user = User.create(name, email, phone)
        return {'data': {'user': created_user.to_json()}}, 201
