# pylint: disable=unused-import
import geojson
from flask import Flask, request
from flask_restx import Api, Resource
from flask_cors import CORS

from models.user import User
from models.target import Target
import fetch_from_museovirasto
import mongo
from util.util import parse_mongo_to_jsonable

app = Flask(__name__)
api = Api(app)

CORS(app)


@api.route('/api/helloworld')
class HelloWorld(Resource):
    def get(self):
        return {'message': 'Hello, World!'}


@api.route('/api/healthcheck')
class HealthCheck(Resource):
    def get(self):
        return {'status': 'ok'}


@api.route('/api/data')
class Data(Resource):
    def get(self):
        with open('data/wreckdata.json', encoding='utf8') as file:
            geojsonfile = geojson.load(file)
        return geojsonfile

    def update(self):
        fetch_from_museovirasto.save_wrecks_geojson('data')
        return {'status': 'update done'}


@api.route('/api/dive')
class Dive(Resource):
    def get(self):
        pass

    def post(self):
        pass


@api.route('/api/users')
class Users(Resource):
    def get(self):
        users = User.objects.values()
        data = [parse_mongo_to_jsonable(user) for user in users]
        return {'data': data}

    def post(self):
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        created_user = User.create(first_name, last_name, email)
        return {'data': {'user': created_user.to_json()}}, 201


@api.route('/api/targets')
class Targets(Resource):
    def get(self):
        targets = Target.objects.values()
        data = [parse_mongo_to_jsonable(target) for target in targets]
        return {'data': data}

    def post(self):
        id = request.form.get('id') or [None]
        name = request.form.get('name') or [None],
        town = request.form.get('town') or [None],
        type = request.form.get('type') or [None],
        x_coordinate = request.form.get('x_coordinate' or [None]),
        y_coordinate = request.form.get('y_coordinate') or [None],
        location_method = request.form.get('location_method') or [None],
        location_accuracy = request.form.get('location_accuracy') or [None],
        url = request.form.get('url') or [None],
        created_at = request.form.get('created_at') or [None],
        created_target = Target.create(
            id[0],
            name[0],
            town[0],
            type[0],
            x_coordinate[0],
            y_coordinate[0],
            location_method[0],
            location_accuracy[0],
            url[0],
            created_at[0]
        )
        return {'data': {'target': created_target.to_json()}}, 201


if __name__ == '__main__':
    app.run(debug=True)
