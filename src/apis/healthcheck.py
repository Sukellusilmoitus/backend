from flask_restx import Namespace, Resource

api = Namespace('healthcheck')


@api.route('/')
class HealthCheck(Resource):
    def get(self):
        return {'status': 'ok'}
