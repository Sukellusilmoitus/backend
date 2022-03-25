from pymodm import MongoModel, fields, errors
from bson.objectid import ObjectId



class User(MongoModel):
    name = fields.CharField(required=True)
    email = fields.CharField(blank=True)
    phone = fields.CharField(blank=True)
    username = fields.CharField(required=True)
    password = fields.CharField(required=True)

    class Meta:
        connection_alias = 'app'
        final = True

    @staticmethod
    def create(name, email, phone, username='None', password='None'):
        user = User(name, email, phone, username, password)
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
            'password': self.password
        }

    def clean(self):
        if not self.email and not self.phone:
            raise errors.ValidationError('Phone or email required')
