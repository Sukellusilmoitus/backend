# pylint: disable=unused-import, invalid-name
import geojson

from models.target import Target
import mongo

with open('data/targetdata.json', encoding='utf-8') as file:
    data = geojson.load(file)

features = data['features']

for feature in features:
    properties = feature['properties'] or 'unknown'
    target_id = properties['id'] or 'unknown'
    name = properties['name'] or 'unknown'
    town = properties['town'] or 'unknown'
    type = properties['type'] or 'unknown'
    location_method = 'unknown'
    location_accuracy = properties['location_accuracy']
    url = properties['url'] or 'unknown'
    created_at = properties['created_at'] or 'unknown'
    is_ancient = properties['is_ancient']
    source = properties['source'] or 'unknown'
    x_coordinate, y_coordinate = feature['geometry']['coordinates']
    is_pending = properties['is_pending']

    Target.create(
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
    )
