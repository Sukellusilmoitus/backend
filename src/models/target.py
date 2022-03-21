# pylint: disable-msg=too-many-arguments
from pymodm import MongoModel, fields

class Target(MongoModel):
    target_id = fields.CharField(primary_key=True)
    name = fields.CharField(required=True)
    town = fields.CharField(required=True)
    type = fields.CharField(required=True)
    x_coordinate = fields.FloatField(required=True)
    y_coordinate = fields.FloatField(required=True)
    location_method = fields.CharField(blank=True)
    location_accuracy = fields.CharField(blank=True)
    url = fields.URLField(blank=True)
    created_at = fields.DateTimeField(blank=True)
    is_ancient = fields.BooleanField(blank=True)
    source = fields.CharField(required=True)
    is_pending = fields.BooleanField(blank=True)

    class Meta:
        connection_alias = 'app'
        final = True

    @staticmethod
    def create(
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
    ):
        target = Target(
            target_id=target_id,
            name=name,
            town=town,
            type=type,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            location_method=location_method,
            location_accuracy=location_accuracy,
            url=url,
            created_at=created_at,
            is_ancient=is_ancient,
            source=source,
            is_pending=is_pending
        )
        target.save()
        return target

    @staticmethod
    def update(
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
    ):

        target = Target.get(target_id)

        if target:
            target.name = name
            target.town = town
            target.type = type
            target.x_coordinate = x_coordinate
            target.y_coordinate = y_coordinate
            target.location_method = location_method
            target.location_accuracy = location_accuracy
            target.url = url
            target.created_at = created_at
            target.is_ancient = is_ancient
            target.source = source
            target.is_pending = is_pending

            target.save()
        return target

    @staticmethod
    def accept(target_id):
        target = Target.get(target_id)
        if target:
            if target.is_pending:
                target.is_pending = False
                target.save()
            return target
        return None

    @staticmethod
    def get(target_id):
        try:
            target = Target.objects.raw({
                '_id': {'$eq': target_id}
            }).first()
            return target
        except Target.DoesNotExist:
            return None

    def to_json(self):
        return {
            'type': 'Feature',
            'properties': {
                'id': str(self.target_id),
                'name': self.name,
                'town': self.town,
                'type': self.type,
                'location_method': self.location_method,
                'location_accuracy': self.location_accuracy,
                'url': self.url,
                'created_at': str(self.created_at).split(' ')[0],
                'is_ancient': self.is_ancient,
                'source': self.source,
                'is_pending': self.is_pending
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [self.x_coordinate, self.y_coordinate]
            }
        }
    def to_json_admin(self):
        return {
            'id': str(self.target_id),
            'name': self.name,
            'town': self.town,
            'type': self.type,
            'location_method': self.location_method,
            'location_accuracy': self.location_accuracy,
            'url': self.url,
            'created_at': str(self.created_at).split(' ')[0],
            'is_ancient': self.is_ancient,
            'source': self.source,
            'coordinates': [self.x_coordinate, self.y_coordinate],
            'is_pending': self.is_pending
            }
