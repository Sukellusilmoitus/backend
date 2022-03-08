# pylint: disable=unused-import
# pylint: disable-msg=too-many-locals
import os
from datetime import datetime
import geojson
from flask import Flask, request
from flask_restx import Api, Resource
from flask_cors import CORS
from pymodm import errors
from models.user import User
from models.target import Target
from models.targetnote import Targetnote
from models.dive import Dive
import fetch_from_museovirasto
import mongo
from util import util

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
        filepath = os.path.join(os.path.dirname(
            __file__), '..', 'data', 'targetdata.json')
        with open(filepath, encoding='utf8') as file:
            geojsonfile = geojson.load(file)
        return geojsonfile

    def update(self):
        fetch_from_museovirasto.save_targets_geojson('data')
        return {'status': 'update done'}


@api.route('/api/dives')
class Dives(Resource):
    def get(self):
        dives = Dive.objects.values()
        data = [util.parse_mongo_to_jsonable(dive) for dive in dives]
        for dive in data:
            diver = User.objects.raw({
                '_id': {'$eq': dive['diver']}
            }).first()
            target = Target.objects.raw({
                '_id': {'$eq': dive['target']}
            }).first()
            dive['diver'] = diver.to_json()
            dive['target'] = target.to_json()
        return {'data': data}

    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        diver_email = data['email']
        diver_phone = data['phone']
        target_id = str(data['locationId'])
        location_correct = data['locationCorrect']
        created_at = datetime.now()
        new_x_coordinate = data['xCoordinate']
        new_y_coordinate = data['yCoordinate']
        new_location_explanation = data['coordinateText']
        change_text = data['changeText']
        miscellaneous = data['miscText']

        try:
            diver = User.objects.raw(
                {'$or':
                 [{'$and': [{'email': {'$eq': diver_email}}, {'email': {'$ne': ''}}]},
                  {'$and': [{'phone': {'$eq': diver_phone}}, {'phone': {'$ne': ''}}]}],
                 }).first()
        except (errors.DoesNotExist, errors.ModelDoesNotExist):
            name = data['name']
            diver = User.create(name, diver_email, diver_phone)
        try:
            target = Target.objects.raw({
                '_id': {'$eq': target_id}
            }).first()
        except errors.DoesNotExist:
            return {'data': 'target not found with given id'}, 406

        created_dive = Dive.create(
            diver,
            target,
            location_correct,
            created_at,
            new_x_coordinate,
            new_y_coordinate,
            new_location_explanation,
            change_text,
            miscellaneous
        )

        return {'data': {'dive': created_dive.to_json()}}, 201


@api.route('/api/targets/newcoordinates')
class TargetsWithNewCoordinates(Resource):
    def get(self):
        dives = Dive.objects.values()
        data = [util.parse_mongo_to_jsonable(dive) for dive in dives]
        targets_with_new_coordinates = []
        for dive in data:
            try:
                if dive['new_y_coordinate']:
                    try:
                        del dive['diver']
                    except KeyError:
                        pass
                    targets_with_new_coordinates.append(dive)
            except KeyError:
                pass

        return {'data': targets_with_new_coordinates}


@api.route('/api/targets/<string:id>')
class SingleTarget(Resource):
    def get(self, id):
        try:
            target = Target.objects.raw({
                '_id': {'$eq': id}
            }).first().to_json()
            dives = Dive.objects.raw({
                'target': {'$eq': target['id']}
            })
            return {'data': {
                'target': target,
                'dives': [dive.to_json() for dive in dives]
            }}
        except errors.DoesNotExist:
            return {'data': None}


@api.route('/api/dives/target/<string:id>')
class SingleDive(Resource):
    def get(self, id):
        dives = Dive.objects.raw({
            'target': {'$eq': id}
        })
        print(dives)
        return {'data': [dive.to_json() for dive in dives]}


@api.route('/api/users')
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


@api.route('/api/targets')
class Targets(Resource):
    def get(self):
        targets = Target.objects.all()
        data = []
        for target in targets:
            data.append(target.to_json())
        return {'features': data}

    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        target_id = data['id']
        divername = data['divername'],
        diver_email = data['email']
        diver_phone = data['phone']
        name = data['targetname'],
        town = data['town'],
        type = data['type'],
        x_coordinate = data['x_coordinate'],
        y_coordinate = data['y_coordinate'],
        location_method = data['location_method'],
        location_accuracy = data['location_accuracy'],
        url = data['url'],
        created_at = data['created_at'],
        is_ancient = data['is_ancient'],
        is_pending = data['is_pending'],
        source = data['source']
        misc_text = data['miscText']

        created_target = Target.create(
            target_id,
            name[0],
            town[0],
            type[0],
            x_coordinate[0],
            y_coordinate[0],
            location_method[0],
            location_accuracy[0],
            url[0],
            created_at[0],
            is_ancient[0],
            source,
            is_pending[0],
        )

        try:
            diver = User.objects.raw(
                {'$or':
                 [{'$and': [{'email': {'$eq': diver_email}}, {'email': {'$ne': ''}}]},
                  {'$and': [{'phone': {'$eq': diver_phone}}, {'phone': {'$ne': ''}}]}],
                 }).first()
        except (errors.DoesNotExist, errors.ModelDoesNotExist):
            diver = User.create(divername, diver_email, diver_phone)

        created_targetnote = Targetnote.create(diver, created_target, misc_text)

        return {'data': {'target': created_target.to_json(),
                         'targetnote': created_targetnote.to_json()}}, 201

@api.route('/api/targets/update')
class TargetsUpdate(Resource):
    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        target_id = data['id']
        name = data['targetname'],
        town = data['town'],
        type = data['type'],
        x_coordinate = data['x_coordinate'],
        y_coordinate = data['y_coordinate'],
        location_method = data['location_method'],
        location_accuracy = data['location_accuracy'],
        url = data['url'],
        created_at = data['created_at'],
        is_ancient = data['is_ancient'],
        is_pending = data['is_pending'],
        source = data['source']

        updated_target = Target.update(
            target_id,
            name[0],
            town[0],
            type[0],
            x_coordinate[0],
            y_coordinate[0],
            location_method[0],
            location_accuracy[0],
            url[0],
            created_at[0],
            is_ancient[0],
            source,
            is_pending[0],
        )

        return {'data': {'target': updated_target.to_json()}}, 201

@api.route('/api/targets/accept')
class TargetsAccept(Resource):
    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        target_id = data['id']

        accepted_target = Target.accept(target_id)

        return {'data': {'target': accepted_target.to_json()}}, 201


if __name__ == '__main__':
    app.run(debug=True)
