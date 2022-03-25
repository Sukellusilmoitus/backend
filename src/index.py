# pylint: disable=unused-import
# pylint: disable-msg=too-many-locals
import os
import json
from datetime import datetime
import geojson
from bson.objectid import ObjectId
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
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from util.config import SECRET_KEY
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
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

@api.route('/api/admin/targets')
class AdminPanelTargets(Resource):
    def get(self):
        start = int(request.args.get('_start'))
        end = int(request.args.get('_end'))
        sortby = request.args.get('_sort', 'ASC')
        order = request.args.get('_order', 'id')
        name = str(request.args.get('name', '')).lower()
        only_user_targets = request.args.get('usertarget', False)
        targets = Target.objects.all()

        targets_json_list = []
        for target in targets:
            if name in target.name.lower() or name is None or name == '':
                if only_user_targets is False:
                    targets_json_list.append(target.to_json_admin())
                else:
                    if target.source == 'ilmoitus':
                        targets_json_list.append(target.to_json_admin())
        try:
            targets_json_list.sort(key=lambda target: target[sortby],
            reverse = order == 'ASC')
        except KeyError:
            pass

        targets_count = len(targets_json_list)
        data = []
        for i in range(start,end):
            try:
                data.append(targets_json_list[i])
            except IndexError:
                pass
        return data, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': targets_count
            }

@api.route('/api/admin/users')
class AdminPanelUsers(Resource):
    def get(self):
        start = int(request.args.get('_start'))
        end = int(request.args.get('_end'))
        sortby = request.args.get('_sort', 'ASC')
        order = request.args.get('_order', 'id')
        name = str(request.args.get('name', '')).lower()

        users = User.objects.all()
        users_json_list = []
        for user in users:
            if name in user.name.lower() or name is None or name == '':
                users_json_list.append(user.to_json())
        try:
            users_json_list.sort(key=lambda user: user[sortby],
            reverse = order == 'ASC')
        except KeyError:
            pass

        users_count = len(users_json_list)
        data = []
        for i in range(start,end):
            try:
                data.append(users_json_list[i])
            except IndexError:
                pass
        return data, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': users_count
            }

@api.route('/api/admin/users/<id>')
class AdminPanelOneUser(Resource):
    def get(self, id):
        users = User.objects.values()
        users2 = [util.parse_mongo_to_jsonable(user) for user in users]
        user_to_return = None
        for user in users2:
            if user['id'] == id:
                user_to_return = user
        return user_to_return, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': '1'
            }
    # pylint: disable=W0613
    def put(self, id):
        data = util.parse_byte_string_to_dict(request.data)
        user_id = data['id']
        name = data['name']
        email = data['email']
        phone = data['phone']
        username = data['username']
        password = data['password']


        updated_user = User.update(
            user_id,
            name,
            email,
            phone,
            username,
            password
        )
        return updated_user.to_json(), 201, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': '1'
            }

@api.route('/api/admin/targets/<id>')
class AdminPanelOneTarget(Resource):
    def get(self, id):
        target = Target.objects.raw({
            '_id': {'$eq': id}
        })
        if target.count() == 1:
            return target.first().to_json_admin(), 200, {
                'Access-Control-Expose-Headers': 'X-Total-Count',
                'X-Total-Count': '1'
                }
        return {}, 410, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': '0'
            }
    # pylint: disable=W0613
    def put(self, id):
        data = util.parse_byte_string_to_dict(request.data)
        target_id = data['id']
        name = data['name']
        town = data['town']
        type = data['type']
        x_coordinate = data['coordinates'][0]
        y_coordinate = data['coordinates'][1]
        location_method = data['location_method']
        location_accuracy = data['location_accuracy']
        url = data['url']
        created_at = data['created_at']
        is_ancient = data['is_ancient']
        source = data['source']
        is_pending = data['is_pending']

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
            is_pending
        )
        return updated_target.to_json_admin(), 201, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': '1'
            }

    def delete(self, id):
        target = Target.objects.raw({
            '_id': {'$eq': id}
        }).first()
        target.delete()
        return target.to_json_admin(), 200

@api.route('/api/admin/dives')
class AdminPanelDives(Resource):
    def get(self):
        start = int(request.args.get('_start'))
        end = int(request.args.get('_end'))
        sortby = request.args.get('_sort', 'ASC')
        order = request.args.get('_order', 'id')

        dives = Dive.objects.all()
        dives_json_list = []
        for dive in dives:
            try:
                dives_json_list.append(dive.to_json_admin())
            except AttributeError:
                pass
        try:
            dives_json_list.sort(key=lambda user: user[sortby],
            reverse = order == 'ASC')
        except KeyError:
            pass

        dives_count = len(dives_json_list)
        data = []
        for i in range(start,end):
            try:
                data.append(dives_json_list[i])
            except IndexError:
                pass
        return data, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': dives_count
            }

@api.route('/api/admin/dives/<id>')
class AdminPanelOneDive(Resource):
    def get(self, id):
        dives = Dive.objects.values()
        dives2 = [util.parse_mongo_to_jsonable(dive) for dive in dives]
        dive_to_return = None
        for dive in dives2:
            if dive['id'] == id:
                dive['diver'] = str(dive['diver']).replace('ObjectId(', '').replace(')', '')
                dive_to_return = dive
        if dive_to_return is not None:
            return dive_to_return, 200, {
                'Access-Control-Expose-Headers': 'X-Total-Count',
                'X-Total-Count': '1'
                }
        return {}, 410, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': '0'
            }

    def put(self, id):
        data = util.parse_byte_string_to_dict(request.data)
        print(data)
        diver = data.get('diver', None).replace('ObjectId(', '').replace(')', '')
        target = data.get('target', None)
        created_at = data.get('created_at', None)
        location_correct = data.get('location_correct', None)
        new_x_coordinate = data.get('new_x_coordinate', None)
        new_y_coordinate = data.get('new_y_coordinate', None)
        new_location_explanation = data.get('new_location_explanation', None)
        change_text = data.get('change_text', None)
        miscellaneous = data.get('miscellaneous', None)

        updated_dive = Dive.update(
            id,
            diver,
            target,
            created_at,
            location_correct,
            new_x_coordinate,
            new_y_coordinate,
            new_location_explanation,
            change_text,
            miscellaneous
        )
        return updated_dive.to_json(), 201, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': '1'
            }

    def delete(self, id):
        dive = Dive.objects.raw({
            '_id': ObjectId(id)
        }).first()
        dive.delete()
        return dive.to_json(), 200

@api.route('/api/admin/pending')
class AdminPanelPendings(Resource):
    def get(self):
        data = []
        targetnotes_all = Targetnote.objects.all()
        for targetnote in targetnotes_all:
            try:
                if targetnote.target.is_pending:
                    data.append(targetnote.to_json_admin())
            except AttributeError:
                pass
        data_count = len(data)
        return data, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': data_count
            }

@api.route('/api/admin/pending/<id>')
class AdminPanelOnePending(Resource):
    def get(self, id):
        targetnotes_all = Targetnote.objects.all()
        targetnote_to_return = None
        for targetnote in targetnotes_all:
            # pylint: disable=W0212
            if targetnote.target.is_pending and str(targetnote._id) == str(id):
                targetnote_to_return = targetnote.to_json_admin()
        return targetnote_to_return, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': '1'
            }
    # pylint: disable=W0613
    def put(self, id):
        data = util.parse_byte_string_to_dict(request.data)
        target_id = data['target_id']
        name = data['name']
        town = data['town']
        type = data['type']
        x_coordinate = data['coordinates'][0]
        y_coordinate = data['coordinates'][1]
        location_method = data['location_method']
        location_accuracy = data['location_accuracy']
        url = data['url']
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

        return updated_target.to_json_admin(), 201, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': '1'}

@api.route('/api/admin/duplicates')
class AdminPanelDuplicates(Resource):
    def get(self):
        start = int(request.args.get('_start'))
        end = int(request.args.get('_end'))

        targets = Target.objects.all()
        cursor = targets.aggregate(
            {'$group': { '_id': {'x_coordinate': '$x_coordinate','y_coordinate': '$y_coordinate'},
            'uniqueIds': {'$addToSet': '$_id'},
            'sources': {'$addToSet': '$source'},
            'count': { '$sum': 1 } } },
            {'$match': {'count' : {'$gt': 1} } }
        )
        duplicates = list(cursor)
        data = []
        for duplicate in duplicates:
            ids = duplicate['uniqueIds']
            sources = duplicate['sources']
            if 'museovirasto' in sources and 'ilmoitus' in sources:
                for id in ids:
                    target = Target.objects.raw({
                        '_id': {'$eq': id}
                    }).first()
                    data.append(target.to_json_admin())

        duplicates_json_list = []
        for i in range(start,end):
            try:
                duplicates_json_list.append(data[i])
            except IndexError:
                pass
        duplicates_count = len(data)
        return data, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': duplicates_count
            }
@api.route('/api/admin/duplicates/<id>')
class AdminPanelOneDuplicates(Resource):
    def get(self, id):
        target = Target.objects.raw({
            '_id': {'$eq': id}
        })
        if target.count() == 1:
            return target.first().to_json_admin(), 200, {
                'Access-Control-Expose-Headers': 'X-Total-Count',
                'X-Total-Count': '1'
                }
        return {}, 410, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': '0'
            }

    def delete(self, id):
        target = Target.objects.raw({
            '_id': {'$eq': id}
        }).first()
        target.delete()
        return target.to_json_admin(), 200

@api.route('/api/targets')
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

@api.route('/api/targets/accept')
class TargetsAccept(Resource):
    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        target_id = data['id']
        accepted_target = Target.accept(target_id)

        return {'data': {'target': accepted_target.to_json()}}, 201

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-ACCESS-TOKEN')
        if token:
            token = request.headers['X-ACCESS-TOKEN']
        else:
            return 'Unauthorized Access!', 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
            user_id = ObjectId(data['user_id'])
            user = User.objects.raw({
                '_id': {'$eq': user_id}
            }).first()
            if not user:
                return 'Unauthorized Access!', 401
        except Exception as e:
            print(e)
            print("ee")
            return 'Unauthorized Access!', 401
        return f(*args, **kwargs)

    return decorated

@api.route('/api/test')
class Test(Resource):
    @token_required
    def get(self):
        return {'message': 'ok'}, 200

@api.route('/api/login')
class Login(Resource):
    def get(self):
        return {}, 200
    
    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        username = data['username']
        password = data['password']
        user = None
        try:
            user = User.objects.raw({
                'username': {'$eq': username}
            }).first()
        except Exception as e:
            print(e)
        
        if not user or not check_password_hash(user.to_json()['password'], password):
            return {'message': 'Väärä käyttäjätunnus tai salasana'}, 200
        
        token = jwt.encode({
            'user_id': user.to_json()['id'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY)

        return {'auth': token}, 200

@api.route('/api/register')
class Register(Resource):
    def post(self):
        data = util.parse_byte_string_to_dict(request.data)
        username = data['username']
        password = data['password']
        user = None
        try:
            user = User.objects.raw({
                'username': {'$eq': username}
            }).first()
        except Exception as e:
            print(e)

        if not user:
            return {}, 200
        return {'message': 'username taken'}, 200


if __name__ == '__main__':
    app.run(debug=True)
