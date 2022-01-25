from flask import Flask, request
from flask_restx import Api, Resource
from flask_cors import CORS
from datetime import date, datetime

import wrecks
import divinglogs

app = Flask(__name__)
api = Api(app)

CORS(app)


@api.route('/api/helloworld')
class HelloWorld(Resource):
    def get(self):
        return {'message': 'Hello, World!'}

@api.route('/api/healthcheck')
class HealthCheck(Resource):
    def get(self):
        return {'status': 'ok'}

@api.route("/api/newdivinglog")
class NewDivingLog(Resource):
    def post(self):
        try:
            diver_id = request.form["diver_id"]
            wreck_id = request.form["wreck_id"]
            location_is_correct = request.form["location_is_correct"]
            x_coordinate = request.form["x_coordinate"]
            y_coordinate = request.form["y_coordinate"]
            new_coordinate_text = request.form["new_coordinate_text"]
            changes_on_wreck = request.form["changes_on_wreck"]
            changes_info = request.form["changes_info"]
        except:
            pass
        now = datetime.now()
        created_at = now.strftime("%d/%m/%Y %H:%M:%S")
        divinglogs.create_new_diving_log(diver_id, wreck_id, location_is_correct,
                                            x_coordinate, y_coordinate, new_coordinate_text,
                                            changes_on_wreck, changes_info, created_at)
        return {'message': 'Data received'}

@api.route("/api/wrecks")
class Wrecks(Resource):
    def get(self):
        all_wrecks = wrecks.get_wrecks()
        return all_wrecks

@api.route("/api/wrecks/<int:id>")
class WreckById(Resource):
    def get(self, id):
        wreck = wrecks.get_wreck_by_id(id)
        return wreck

if __name__ == '__main__':
    app.run(debug=True)
