import os
from flask import Flask
from flask_cors import CORS

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Настройка CORS крайне важна для работы fetch с другого порта
    CORS(app) 

    # ... остальной код регистрации ...
    from .routes import bp as planner_bp
    app.register_blueprint(planner_bp, url_prefix='/planner')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5001, debug=True)