import os
from flask import Flask
from . import dns

def create_app():
    app = Flask(__name__)

    # where your agents.json lives
    agents_path = os.getenv(
        "AGENTS_JSON_PATH",
        "./dns.json"
    )

    app.config["AGENTS_JSON_PATH"] = agents_path

    # Load agents at startup
    dns.load_agents_from_file(agents_path)

    # Register blueprint
    app.register_blueprint(dns.registry_bp, url_prefix="/registry")

    return app