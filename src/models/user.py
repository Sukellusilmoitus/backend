from pymodm import MongoModel, fields, errors
from bson.objectid import ObjectId



class User(MongoModel):
    name = fields.CharField(required=True)
    email = fields.CharField(blank=True)
    phone = fields.CharField(blank=True)

    class Meta:
        connection_alias = 'app'
        final = True

    @staticmethod
    def create(name, email, phone):
        user = User(name, email, phone)
        user.save()
        return user

    @staticmethod
    def update(
        user_id,
        name,
        email,
        phone
    ):
        user = User.objects.raw({
            '_id': ObjectId(user_id)
        }).first()

        user.name = name
        user.email = email
        user.phone = phone

        user.save()
        return user

    def to_json(self):
        return {
            'id': str(self._id) or None,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }

    def clean(self):
        if not self.email and not self.phone:
            raise errors.ValidationError('Phone or email required')
