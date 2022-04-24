from flask import request
from flask_restx import Namespace, Resource
from bson.objectid import ObjectId
from models.target import Target
from models.user import User
from models.dive import Dive
from models.targetnote import Targetnote
from util import util
from util.util import admin_required

api = Namespace('admin')


@api.route('/targets')
class AdminPanelTargets(Resource):
    @admin_required
    def get(self):
        """api route for adminpanel targets page

        Returns:
            code 200: return 200, targets data and X-Total-Count
        """
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
    @admin_required
    def get(self):
        """api route for adminpanel users page

        Returns:
            code 200: return 200, users data, X-Total-Count
        """
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
    @admin_required
    def get(self, id):
        """api route for adminpanel user editing page

        Args:
            id (str): user id

        Returns:
            code 200: return 200, user data if found or None and X-Total-Count: 1
        """
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
    @admin_required
    def put(self, id):
        """api route to handle adminpanel user updates

        Args:
            id (str): user id

        Returns:
            code 201: return 200, updated user data as json and and X-Total-Count: 1
        """
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
    @admin_required
    def get(self, id):
        """api route for adminpanel target editing page

        Args:
            id (str): target id

        Returns:
            code 200: return 200 and the taget data as admin json if target found
            code 410: return 410 if target not found
        """
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
    @admin_required
    def put(self, id):
        """api route to handle adminpanel target updates

        Args:
            id (str): target id

        Returns:
            code 201: return 201 and updated target data as json admin
        """
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

    @admin_required
    def delete(self, id):
        """api route to handle adminpanel target delete request

        Args:
            id (str): target id

        Returns:
            code 200: return 200 after delete
        """
        target = Target.objects.raw({
            '_id': {'$eq': id}
        }).first()
        target.delete()
        return target.to_json_admin(), 200


@api.route('/dives')
class AdminPanelDives(Resource):
    @admin_required
    def get(self):
        """api route for adminpanel dives page

        Returns:
            code 200: return 200, dives data and X-Total-Count
        """
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
    @admin_required
    def get(self, id):
        """api route for adminpanel dives editing page

        Args:
            id (str): dive id

        Returns:
            code 200: return 200 and dive data if dive found by id
            code 410: return 410 if dive not found
        """
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

    @admin_required
    def put(self, id):
        """api route to handle adminpanel dives updates

        Args:
            id (str): dive id

        Returns:
            code 201: return 201, updated dive as json admin and X-Total-Count
        """
        data = util.parse_byte_string_to_dict(request.data)
        diver = data.get('diver', None).replace(
            'ObjectId(', '').replace(')', '')
        target = data.get('target', None)
        created_at = data.get('created_at', None)
        divedate = data.get('divedate', None)
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
            divedate,
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

    @admin_required
    def delete(self, id):
        """api route to handle adminpanel dive delete

        Args:
            id (str): dive id

        Returns:
            code 200: return 200
        """
        dive = Dive.objects.raw({
            '_id': ObjectId(id)
        }).first()
        dive.delete()
        return dive.to_json(), 200


@api.route('/pending')
class AdminPanelPendings(Resource):
    @admin_required
    def get(self):
        """api route for adminpanel pending page

        Returns:
            code 200: return 200, pending targets data and X-Total-Count
        """
        start = int(request.args.get('_start') or 0)
        end = int(request.args.get('_end') or 10)
        sortby = request.args.get('_sort', 'ASC')
        order = request.args.get('_order', 'id')

        data = []
        targetnotes_all = Targetnote.objects.all()
        for targetnote in targetnotes_all:
            try:
                if targetnote.target.is_pending:
                    data.append(targetnote.to_json_admin())
            except AttributeError:
                pass
        try:
            data.sort(key=lambda target: target[sortby],
                                 reverse=order == 'ASC')
        except KeyError:
            pass
        pending_data = []
        for i in range(start, end):
            try:
                pending_data.append(data[i])
            except IndexError:
                pass
        data_count = len(data)

        return pending_data, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': data_count
        }


@api.route('/pending/<id>')
class AdminPanelOnePending(Resource):
    @admin_required
    def get(self, id):
        """api route for adminpanel pending editing page

        Args:
            id (str): targetnote id

        Returns:
            code 200: return 200, target data if found by id or None, X-Total-Count
        """
        targetnotes_all = Targetnote.objects.all()
        targetnote_to_return = None
        for targetnote in targetnotes_all:
            # pylint: disable=W0212, W0702
            try:
                if targetnote.target.is_pending and str(targetnote._id) == str(id):
                    targetnote_to_return = targetnote.to_json_admin()
            except:
                pass
        return targetnote_to_return, 200, {
            'Access-Control-Expose-Headers': 'X-Total-Count',
            'X-Total-Count': '1'
        }
    # pylint: disable=W0613

    @admin_required
    def put(self, id):
        """api route to handle adminpanel pending updates

        Args:
            id (str): targetnote_id

        Returns:
            code 201: return 201, updated targe as json admin and X-Total-Count
        """
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
    @admin_required
    def get(self):
        """api route for adminpanel duplicates page

        Returns:
            code 200: return 200, duplicates targets data and X-Total-Count
        """
        start = int(request.args.get('_start') or 0)
        end = int(request.args.get('_end') or 10)
        sortby = request.args.get('_sort', 'ASC')
        order = request.args.get('_order', 'id')

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
        try:
            data.sort(key=lambda target: target[sortby],
                                 reverse=order == 'ASC')
        except KeyError:
            pass
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
    @admin_required
    def get(self, id):
        """api route for adminpanel duplicates editing page

        Args:
            id (str): target id

        Returns:
            code 200: return 200, target data as json admin and X-Total-Count
            code 410: return 410 if target not found by id
        """
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

    @admin_required
    def delete(self, id):
        """api route for adminpanel duplicate delete

        Args:
            id (str): target id

        Returns:
            code 200: return 200
        """
        target = Target.objects.raw({
            '_id': {'$eq': id}
        }).first()
        target.delete()
        return target.to_json_admin(), 200
