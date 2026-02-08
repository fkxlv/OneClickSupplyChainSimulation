import os
from flask import Flask
from flask_cors import CORS

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Настройка CORS крайне важна для работы fetch с другого порта
    CORS(app, resources={r"/*": {"origins": "*"}}) 

    from . import routes
    app.register_blueprint(routes.manufacturer_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5004, debug=True)