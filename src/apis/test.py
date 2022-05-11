from flask_restx import Namespace, Resource
from util.util import token_required

api = Namespace('test')


@api.route('/')
class Test(Resource):
    @token_required
    def get(self):
        return {'message': 'ok'}, 200
