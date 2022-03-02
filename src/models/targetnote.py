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
