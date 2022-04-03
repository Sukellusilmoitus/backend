from flask import request
from flask_restx import Namespace, Resource
from datetime import datetime, timedelta
from pymodm import errors
from werkzeug.security import check_password_hash
import jwt
from models.user import User
from util import util
from util.config import SECRET_KEY

api = Namespace('login')


@api.route('/')
class Login(Resource):
    def get(self):
        return {}, 200

    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        username = data.get('username', None)
        password = data.get('password', None)
        user = None
        if username is None or password is None:
            return {}, 400
        try:
            user = User.objects.raw({
                'username': {'$eq': username}
            }).first()
        except (errors.DoesNotExist, errors.ModelDoesNotExist):
            return {'message': 'Väärä käyttäjätunnus tai salasana'}, 200

        if not user or not check_password_hash(user.to_json()['password'], password):
            return {'message': 'Väärä käyttäjätunnus tai salasana'}, 200

        token = jwt.encode({
            'user_id': user.to_json()['id'],
            'username': user.username,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY)
        return {'auth': token}, 200
