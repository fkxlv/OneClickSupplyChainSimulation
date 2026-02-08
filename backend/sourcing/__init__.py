import os

from flask import Flask, request
from flask_cors import CORS
from flask_marshmallow import Marshmallow

app = Flask(__name__, instance_relative_config=True)
cors = CORS(app)
ma = Marshmallow(app)

app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'server.sqlite')
)

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

@app.route('/sourcing', methods=['POST'])
def index():
    data = request.get_json()
    print(data["status"])
    return "THE SOURCING AGENT!"

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
    #return app