from pymodm import MongoModel, fields


class User(MongoModel):
    name = fields.CharField(required=True)
    email = fields.CharField(required=True)
    phone = fields.CharField()

    class Meta:
        connection_alias = 'app'
        final = True

    @staticmethod
    def create(name, email, phone):
        user = User(name, email, phone)
        user.save()
        return user

    def to_json(self):
        return {
            'id': str(self._id) or None,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }
