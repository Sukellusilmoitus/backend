import os
import geojson
from flask_restx import Namespace, Resource
from util import fetch_from_museovirasto

api = Namespace('data')


@api.route('/')
class Data(Resource):
    def get(self):
        filepath = os.path.join(os.path.dirname(
            __file__), '..', '..', 'data', 'targetdata.json')
        with open(filepath, encoding='utf8') as file:
            geojsonfile = geojson.load(file)
        return geojsonfile

    def update(self):
        fetch_from_museovirasto.save_targets_geojson('data')
        return {'status': 'update done'}
