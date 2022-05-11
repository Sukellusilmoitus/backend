from pymodm import MongoModel, fields, errors
from bson.objectid import ObjectId


class User(MongoModel):
    name = fields.CharField(required=True)
    email = fields.CharField(blank=True)
    phone = fields.CharField(blank=True)
    username = fields.CharField(blank=True)
    password = fields.CharField(blank=True)
    admin = fields.BooleanField(blank=True)

    class Meta:
        connection_alias = 'app'
        final = True

    @staticmethod
    def create(name, email, phone, username=None, password=None):
        user = User(name, email, phone, username, password, False)
        user.save()
        return user

    @staticmethod
    def update(
        user_id,
        name,
        email,
        phone,
        username,
        password
    ):
        user = User.objects.raw({
            '_id': ObjectId(user_id)
        }).first()

        user.name = name
        user.email = email
        user.phone = phone
        user.username = username
        user.password = password

        user.save()
        return user

    def to_json(self):
        return {
            'id': str(self._id) or None,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'username': self.username,
            'password': self.password,
            'admin': self.admin
        }

    def clean(self):
        if not self.email and not self.phone:
            raise errors.ValidationError('Phone or email required')

    @staticmethod
    def get_by_email_phone(user_email, user_phone):
        """
        Returns matching user by email or phone number
        Looks first from registered users
        """
        try:
            user = User.objects.raw(
                {'$or':
                    [
                        {'$and': [{'username': {'$ne': None}}, {
                            'email': {'$eq': user_email}}, {'email': {'$ne': ''}}]},
                        {'$and': [{'username': {'$ne': None}}, {
                            'phone': {'$eq': user_phone}}, {'phone': {'$ne': ''}}]}
                    ],
                 }).first()
            return user
        except (User.DoesNotExist, errors.ModelDoesNotExist, errors.DoesNotExist):
            try:
                user = User.objects.raw(
                    {'$or':
                        [
                            {'$and': [{'email': {'$eq': user_email}}, {'email': {'$ne': ''}}]},
                            {'$and': [{'phone': {'$eq': user_phone}}, {'phone': {'$ne': ''}}]}
                        ],
                    }).first()
                return user
            except (User.DoesNotExist, errors.ModelDoesNotExist, errors.DoesNotExist):
                return None

    @staticmethod
    def get_all_test(preservable_usernames):
        """
        Returns all users except the users with usernames given in parameter list
        """
        try:
            users = User.objects.raw({
                'username': {'$nin': preservable_usernames}
            }).all()
            return users
        except User.DoesNotExist:
            return None
