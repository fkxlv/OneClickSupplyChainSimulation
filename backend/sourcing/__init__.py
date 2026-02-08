import os

from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from . import routes

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    cors = CORS(app)

    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    app.register_blueprint(routes.sourcing_bp, url_prefix="/sourcing")

    @app.route('/')
    def index():
        return "THE SOURCING AGENT!"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5002, debug=True)