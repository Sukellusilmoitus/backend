from datetime import datetime, timedelta
import jwt
from flask import request
from flask_restx import Namespace, Resource
from models.user import User
from util import util
from util.util import token_required
from util.config import SECRET_KEY

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

    @token_required
    def put(self):
        data = util.parse_byte_string_to_dict(request.data)
        username = data['username']
        user = User.objects.raw({'username': {'$eq': username}}).first()

        user_id = user.to_json()['id']
        password = user.to_json()['password']
        name = data['name']
        email = data['email']
        phone = data['phone']

        updated_user = User.update(
            user_id,
            name,
            email,
            phone,
            username,
            password
        ).to_json()

        token = jwt.encode({
            'user_id': updated_user['id'],
            'username': updated_user['username'],
            'name': name,
            'email': email,
            'phone': phone,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY)
        return {'auth': token}, 201
