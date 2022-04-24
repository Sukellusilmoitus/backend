from flask_restx import Namespace, Resource
from util.util import admin_required

api = Namespace('testadmin')

@api.route('/')
class TestAdmin(Resource):
    @admin_required
    def get(self):
        return {'message': 'ok'}, 200