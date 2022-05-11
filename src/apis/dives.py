from datetime import datetime
from flask_restx import Namespace, Resource
from flask import request
from pymodm import errors
from models.dive import Dive
from models.user import User
from models.target import Target
from util import util

api = Namespace('dives')


@api.route('/')
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
        divedate = datetime.strptime(data['diveDate'], '%d.%m.%Y')
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
            divedate,
            new_x_coordinate,
            new_y_coordinate,
            new_location_explanation,
            change_text,
            miscellaneous
        )

        return {'data': {'dive': created_dive.to_json()}}, 201


@api.route('/user/<string:username>')
class UserDives(Resource):
    @util.token_required
    def get(self, username):
        try:
            diver = User.objects.raw({'username': {'$eq': username}}).first()
        except (errors.DoesNotExist, errors.ModelDoesNotExist):
            return {'message': 'user not found'}, 200
        dives = Dive.objects.raw({
            '$query': {'diver': {'$eq': diver.pk}},
            '$orderby': {'divedate': -1}
        })
        return {'data': [dive.to_json() for dive in dives]}, 200


@api.route('/target/<string:id>')
class SingleDive(Resource):
    def get(self, id):
        dives = Dive.objects.raw({
            '$query': {'target': {'$eq': id}},
            '$orderby': {'divedate': -1}
        })
        return {'data': [dive.to_json() for dive in dives]}
