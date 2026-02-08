import os
from flask import Flask
from flask_cors import CORS

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app) # Разрешаем запросы с фронтенда

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'server.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # --- РЕГИСТРАЦИЯ РОУТОВ ---
    from .routes import bp as planner_bp
    app.register_blueprint(planner_bp, url_prefix='/planner')

    @app.route('/')
    def index():
        return "Planner Agent is Online 🟢"
    
    return app