from pymodm import MongoModel, fields
from models.target import Target
from models.user import User
from bson.objectid import ObjectId

class Dive(MongoModel):
    diver = fields.ReferenceField(User)
    target = fields.ReferenceField(Target)
    created_at = fields.DateTimeField()
    location_correct = fields.BooleanField()
    new_x_coordinate = fields.CharField(blank=True)
    new_y_coordinate = fields.CharField(blank=True)
    new_location_explanation = fields.CharField(blank=True)
    change_text = fields.CharField(blank=True)
    miscellaneous = fields.CharField(blank=True)

    class Meta:
        connection_alias = 'app'
        final = True

    @staticmethod
    def create(
        diver,
        target,
        location_correct,
        created_at,
        new_x_coordinate=None,
        new_y_coordinate=None,
        new_location_explanation=None,
        change_text=None,
        miscellaneous=None
    ):
        dive = Dive(
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
        dive.save()
        return dive
    
    @staticmethod
    def update(
        dive_id,
        diver,
        target,
        created_at,
        location_correct,
        new_x_coordinate,
        new_y_coordinate,
        new_location_explanation,
        change_text,
        miscellaneous
    ):
        dive = Dive.objects.raw({
            '_id': ObjectId(dive_id)
        }).first()

        dive.diver = diver
        dive.target = target
        dive.created_at = created_at
        dive.location_correct = location_correct
        dive.new_x_coordinate = new_x_coordinate
        dive.new_y_coordinate = new_y_coordinate
        dive.new_location_explanation = new_location_explanation
        dive.change_text = change_text
        dive.miscellaneous = miscellaneous

        dive.save()
        return dive

    def to_json(self):
        return {
            'id': str(self._id) or None,
            'diver': self.diver.to_json(),
            'target': self.target.to_json(),
            'location_correct': self.location_correct,
            'created_at': str(self.created_at),
            'miscellanious': self.miscellaneous,
            'change_text': self.change_text,
            'new_x_coordinate': self.new_x_coordinate,
            'new_y_coordinate': self.new_y_coordinate,
            'new_location_explanation': self.new_location_explanation,
        }
