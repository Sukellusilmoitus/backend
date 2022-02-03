from pymodm import MongoModel, fields


class Target(MongoModel):
    id = fields.CharField(primary_key=True)
    name = fields.CharField()
    town = fields.CharField()
    type = fields.CharField()
    x_coordinate = fields.FloatField()
    y_coordinate = fields.FloatField()
    location_method = fields.CharField(blank=True)
    location_accuracy = fields.CharField(blank=True)
    url = fields.URLField()
    created_at = fields.DateTimeField()
    is_ancient = fields.BooleanField(blank=True)
    source = fields.CharField()

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
        source
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
            source=source
        )
        target.save()
        return target

    def to_json(self):
        return {
            'id': self.target_id,
            'name': self.name,
            'town': self.town,
            'type': self.type,
            'x_coordinate': self.x_coordinate,
            'y_coordinate': self.y_coordinate,
            'location_method': self.location_method,
            'location_accuracy': self.location_accuracy,
            'url': self.url,
            'created_at': str(self.created_at).split(' ')[0],
            'is_ancient': self.is_ancient,
            'source': self.source
        }
