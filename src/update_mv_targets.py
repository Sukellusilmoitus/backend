# pylint: disable=unused-import, invalid-name
import geojson
import fetch_from_museovirasto
from models.target import Target
import mongo


class Updater:

    def __init__(self):
        pass

    def update_data_file(self, path):
        result = fetch_from_museovirasto.save_targets_geojson(path)
        if len(result['errors']) == 0:
            return {'status': 'file update done'}
        else:
            return {'status': 'file update failed', 'errors': result['errors']}

    def update_targets_from_file_to_db(self, path):
        with open(path, encoding='utf-8') as file:
            data = geojson.load(file)

        features = data['features']

        checked = 0
        changed = 0
        new = 0

        for feature in features:
            properties = feature['properties'] or 'unknown'
            target_id = str(properties['id']) or 'unknown'
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
            is_pending = False

            target = Target.get(target_id)

            if target:
                if (target.name != name
                    or target.town != town
                    or target.type != type
                    or target.x_coordinate != x_coordinate
                    or target.y_coordinate != y_coordinate
                    or target.location_method != location_method
                    or target.location_accuracy != location_accuracy
                    or target.url != url
                    or str(target.created_at).split(' ')[0] != created_at
                    or target.is_ancient != is_ancient
                    or target.source != source
                    or target.is_pending != is_pending):

                    Target.update(
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

                    changed += 1

            else:
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
            checked += 1

        return {'checked': checked, 'changed': changed, 'new': new}

    def update_targets(self):
        return {'data file': self.update_data_file('data'),
                'saving to database': self.update_targets_from_file_to_db('data/targetdata.json')}

if __name__ == '__main__':
    updater = Updater()
    update_result = updater.update_targets()
    print('UPDATE FINISHED')
    print('Target data file update: ', update_result['data file'])
    print('Saving targets to database: ', update_result['saving to database'])
