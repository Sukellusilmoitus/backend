from flask import request
from flask_restx import Namespace, Resource
from bson.objectid import ObjectId
from models.target import Target
from models.user import User
from models.dive import Dive
from models.targetnote import Targetnote
from util import util

api = Namespace('admin')


@api.route('/targets')
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
                                   reverse=order == 'ASC')
        except KeyError:
            pass

        targets_count = len(targets_json_list)
        data = []
        for i in range(start, end):
            try:
                data.append(targets_json_list[i])
            except IndexError:
                pass
        return data, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': targets_count
        }


@api.route('/users')
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
                                 reverse=order == 'ASC')
        except KeyError:
            pass

        users_count = len(users_json_list)
        data = []
        for i in range(start, end):
            try:
                data.append(users_json_list[i])
            except IndexError:
                pass
        return data, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': users_count
        }


@api.route('/users/<id>')
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


@api.route('/targets/<id>')
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


@api.route('/dives')
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
                                 reverse=order == 'ASC')
        except KeyError:
            pass

        dives_count = len(dives_json_list)
        data = []
        for i in range(start, end):
            try:
                data.append(dives_json_list[i])
            except IndexError:
                pass
        return data, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': dives_count
        }


@api.route('/dives/<id>')
class AdminPanelOneDive(Resource):
    def get(self, id):
        dives = Dive.objects.values()
        dives2 = [util.parse_mongo_to_jsonable(dive) for dive in dives]
        dive_to_return = None
        for dive in dives2:
            if dive['id'] == id:
                dive['diver'] = str(dive['diver']).replace(
                    'ObjectId(', '').replace(')', '')
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
        diver = data.get('diver', None).replace(
            'ObjectId(', '').replace(')', '')
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


@api.route('/pending')
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


@api.route('/pending/<id>')
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


@api.route('/duplicates')
class AdminPanelDuplicates(Resource):
    def get(self):
        start = int(request.args.get('_start'))
        end = int(request.args.get('_end'))

        targets = Target.objects.all()
        cursor = targets.aggregate(
            {'$addFields': {
                'rounded_x': {'$round': ['$x_coordinate', 4]},
                'rounded_y': {'$round': ['$y_coordinate', 4]}
            }
            },
            {'$group': {'_id': {'x_coordinate': '$rounded_x', 'y_coordinate': '$rounded_y'},
                        'uniqueIds': {'$addToSet': '$_id'},
                        'sources': {'$addToSet': '$source'},
                        'count': {'$sum': 1}}},
            {'$match': {'count': {'$gt': 1}}}
        )
        duplicates = list(cursor)
        data = []
        for duplicate in duplicates:
            ids = duplicate['uniqueIds']
            sources = duplicate['sources']
            if 'museovirasto' in sources and 'ilmoitus' in sources:
                for id in ids:
                    target = Target.get(id)
                    data.append(target.to_json_admin())

        duplicates_json_list = []
        for i in range(start, end):
            try:
                duplicates_json_list.append(data[i])
            except IndexError:
                pass
        duplicates_count = len(data)
        return data, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': duplicates_count
        }


@api.route('/duplicates/<id>')
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
