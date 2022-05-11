from flask import request
from flask_restx import Namespace, Resource
from pymodm import errors
from werkzeug.security import generate_password_hash
from models.user import User
from util import util

api = Namespace('register')


@api.route('/')
class Register(Resource):
    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        name = data['name']
        email = data.get('email', 'None')
        phone = data.get('phone', 'None')
        username = data['username']
        password = generate_password_hash(data['password'])
        user = None
        try:
            user = User.objects.raw({
                'username': {'$eq': username}
            }).first()
        except (errors.DoesNotExist, errors.ModelDoesNotExist):
            user = None

        if not user:
            if not email and not phone:
                return {}, 400
            User.create(
                name=name, email=email, phone=phone, username=username, password=password
            )
            return {}, 200
        return {'message': 'username taken'}, 200
