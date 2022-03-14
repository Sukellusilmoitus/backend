# pylint: disable=unused-import, invalid-name
import geojson
import fetch_from_museovirasto

from models.target import Target
import mongo

def update_data_file(path):
    fetch_from_museovirasto.save_targets_geojson(path)
    return {'status': 'update done'}

def update_targets_from_file_to_db(path):
    with open(path, encoding='utf-8') as file:
        data = geojson.load(file)

    features = data['features']

    updated = 0
    changed = 0
    new = 0

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
        is_pending = properties['is_pending'] or False

        #update returns None if target does not exists
        target = Target.update(
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
            is_pending)

        if not target:
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
            new += 1
        else:
            if (target.name != name
               or target.town != town
               or target.type != type
               or target.x_coordinate != x_coordinate
               or target.y_coordinate != y_coordinate
               or target.location_method != location_method
               or target.location_accuracy != location_accuracy
               or target.url != url
               or target.created_at != created_at
               or target.is_ancient != is_ancient
               or target.source != source
               or target.is_pending != is_pending):
                changed += 1
            updated += 1

    return {'updated': updated, 'changed': changed, 'new': new}

def update_targets():
    update_data_file('data')
    update_targets_from_file_to_db('data/targetdata.json')
