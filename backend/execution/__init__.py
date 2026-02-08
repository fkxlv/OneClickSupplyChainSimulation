import os

from flask import Flask
from flask_cors import CORS
from backend import *

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

    from . import routes

    app.register_blueprint(routes.execution_bp, url_prefix="/execution")

    @app.route('/')
    def index():
        return "THE EXECUTION AGENT!"
    
    return app