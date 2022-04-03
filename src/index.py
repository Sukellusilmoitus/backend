# pylint: disable=unused-import
# pylint: disable-msg=too-many-locals
from flask import Flask
from flask_cors import CORS
import mongo
from util.config import SECRET_KEY
from apis import api

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

CORS(app)

api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
