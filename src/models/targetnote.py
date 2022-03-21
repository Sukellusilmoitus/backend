from pymodm import MongoModel, fields
from models.target import Target
from models.user import User


class Targetnote(MongoModel):
    diver = fields.ReferenceField(User, required=True)
    target = fields.ReferenceField(Target, required=True)
    created_at = fields.DateTimeField()
    miscellaneous = fields.CharField(blank=True)

    class Meta:
        connection_alias = 'app'
        final = True

    @staticmethod
    def create(
        diver,
        target,
        miscellaneous=None
    ):
        targetnote = Targetnote(
            diver,
            target,
            target.created_at,
            miscellaneous
        )
        targetnote.save()
        return targetnote

    def to_json(self):
        return {
            'diver': self.diver.to_json(),
            'target': self.target.to_json(),
            'miscellaneous': self.miscellaneous
        }
    def to_json_admin(self):
        return {
            'id': str(self._id),
            # pylint: disable=W0212
            'target_id': str(self.target.target_id),
            # pylint: disable=W0212
            'user_id': str(self.diver._id),
            'name': self.target.name,
            'town': self.target.town,
            'type': self.target.type,
            'location_method': self.target.location_method,
            'location_accuracy': self.target.location_accuracy,
            'url': self.target.url,
            'created_at': str(self.target.created_at).split(' ')[0],
            'is_ancient': self.target.is_ancient,
            'source': self.target.source,
            'coordinates': [self.target.x_coordinate, self.target.y_coordinate],
            'is_pending': self.target.is_pending,
            'miscellaneous': self.miscellaneous
        }
