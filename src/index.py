from flask import Flask
from flask_cors import CORS
from util.mongo import connect_to_db
from util.config import SECRET_KEY
from apis import api

connect_to_db()

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

CORS(app)

api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
