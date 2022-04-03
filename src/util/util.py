import ast
from functools import wraps
from flask import request
import jwt
from bson.objectid import ObjectId
from pymodm import errors
from models.user import User
from util.config import SECRET_KEY


def parse_mongo_to_jsonable(item):
    if item.get('_id'):
        item['id'] = str(item['_id'])
        del item['_id']
    if 'created_at' in item:
        item['created_at'] = _datetime_to_valid_string(item['created_at'])
    return item


def _datetime_to_valid_string(date):
    return str(date).split(' ')[0]


def parse_byte_string_to_dict(value):
    dict_str = value.decode('UTF-8')
    dict_str = dict_str.replace('true', 'True')
    dict_str = dict_str.replace('false', 'False')
    dict_str = dict_str.replace('null', 'None')
    data = ast.literal_eval(dict_str)
    return data


def token_required(wrapped):
    @wraps(wrapped)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-ACCESS-TOKEN')
        if token:
            token = request.headers['X-ACCESS-TOKEN']
        else:
            return 'Unauthorized Access!', 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms='HS256')
            user_id = ObjectId(data['user_id'])
            user = User.objects.raw({
                '_id': {'$eq': user_id}
            }).first()
            if not user:
                return 'Unauthorized Access!', 401
        except (errors.DoesNotExist, errors.ModelDoesNotExist):
            return 'Unauthorized Access!', 401
        return wrapped(*args, **kwargs)

    return decorated
