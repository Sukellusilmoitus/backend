# pylint: disable=too-many-locals
from flask import request
from flask_restx import Namespace, Resource
from pymodm import errors
from models.target import Target
from models.dive import Dive
from models.user import User
from models.targetnote import Targetnote
from util import util

api = Namespace('targets')


@api.route('/newcoordinates')
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


@api.route('/user/<string:username>')
class UserTargets(Resource):
    @util.token_required
    def get(self, username):
        try:
            diver = User.objects.raw({'username': {'$eq': username}}).first()
        except (errors.DoesNotExist, errors.ModelDoesNotExist):
            return {'message': 'user not found'}, 200
        targetnotes = Targetnote.objects.raw({
            '$query': {'diver': {'$eq': diver.pk}},
            '$orderby': {'created_at': -1}
        })
        return {'data': [targetnote.to_json() for targetnote in targetnotes]}, 200


@api.route('/<string:id>')
class SingleTarget(Resource):
    def get(self, id):
        try:
            target = Target.objects.raw({
                '_id': {'$eq': id}
            }).first().to_json()
            dives = Dive.objects.raw({
                '$query': {'target': {'$eq': target['properties']['id']}},
                '$orderby': {'divedate': -1}
            })
            return {'data': {
                'target': target,
                'dives': [dive.to_json() for dive in dives]
            }}
        except errors.DoesNotExist:
            return {'data': None}


@api.route('/')
class Targets(Resource):
    def get(self):
        targets = Target.objects.raw({
            'is_pending': {'$ne': True}
        }).all()
        data = []
        for target in targets:
            data.append(target.to_json())
        targets_count = len(data)
        return {'features': data}, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': targets_count
        }

    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        target_id = data['id']
        divername = data['divername']
        diver_email = data['email']
        diver_phone = data['phone']
        name = data['targetname']
        town = data['town']
        type = data['type']
        x_coordinate = data['x_coordinate']
        y_coordinate = data['y_coordinate']
        location_method = data['location_method']
        location_accuracy = data['location_accuracy']
        url = data['url']
        created_at = data['created_at']
        is_ancient = data['is_ancient']
        is_pending = True
        source = data['source']
        misc_text = data['miscText']
        created_target = Target.create(
            target_id,
            name,
            town,
            type,
            x_coordinate,
            y_coordinate,
            location_method,
            location_accuracy,
            url,
            created_at,
            is_ancient,
            source,
            is_pending,
        )

        diver = User.get_by_email_phone(diver_email, diver_phone)
        if not diver:
            diver = User.create(divername, diver_email, diver_phone)

        created_targetnote = Targetnote.create(
            diver, created_target, misc_text)
        return {'data': {'target': created_target.to_json(),
                         'targetnote': created_targetnote.to_json()}}, 201


@api.route('/update')
class TargetsUpdate(Resource):
    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        target_id = data['id']
        name = data['targetname']
        town = data['town']
        type = data['type']
        x_coordinate = data['x_coordinate']
        y_coordinate = data['y_coordinate']
        location_method = data['location_method']
        location_accuracy = data['location_accuracy']
        url = data['url'],
        created_at = data['created_at']
        is_ancient = data['is_ancient']
        is_pending = data['is_pending']
        source = data['source']

        updated_target = Target.update(
            target_id,
            name,
            town,
            type,
            x_coordinate,
            y_coordinate,
            location_method,
            location_accuracy,
            url,
            created_at,
            is_ancient,
            source,
            is_pending,
        )

        return {'data': {'target': updated_target.to_json()}}, 201


@api.route('/accept')
class TargetsAccept(Resource):
    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        target_id = data['id']
        accepted_target = Target.accept(target_id)

        return {'data': {'target': accepted_target.to_json()}}, 201
