import os
from flask import Flask
from . import dns

def create_app():
    app = Flask(__name__)
    
    dns_json_path = os.path.join(os.path.dirname(__file__), "dns.json")
    app.config["AGENTS_JSON_PATH"] = dns_json_path

    # Load agents at startup
    dns.load_agents_from_file(dns_json_path)

    # Register blueprint
    app.register_blueprint(dns.registry_bp, url_prefix="/registry")

    return app