from pymodm import MongoModel, fields
from models.target import Target
from models.user import User


class Dive(MongoModel):
    diver = fields.ReferenceField(User)
    target = fields.ReferenceField(Target)
    created_at = fields.DateTimeField()
    location_correct = fields.BooleanField()
    miscellaneous = fields.CharField(blank=True)
    new_x_coordinates = fields.CharField(blank=True)
    new_y_coordinates = fields.CharField(blank=True)

    class Meta:
        connection_alias = 'app'
        final = True

    @staticmethod
    def create(
            diver,
            target,
            location_correct,
            created_at,
            miscellaneous,
            new_x_coordinates=None,
            new_y_coordinates=None):
        dive = Dive(
            diver,
            target,
            created_at,
            location_correct,
            miscellaneous,
            new_x_coordinates,
            new_y_coordinates)
        dive.save()
        return dive

    def to_json(self):
        return {
            'id': str(self._id) or None,
            'diver': self.diver.to_json(),
            'target': self.target.to_json(),
            'location_correct': self.location_correct,
            'created_at': str(self.created_at),
            'miscellanious': self.miscellaneous
        }
