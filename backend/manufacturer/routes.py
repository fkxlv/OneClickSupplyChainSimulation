from flask import request, Blueprint, make_response

manufacturer_bp = Blueprint("manufacturer", __name__)

@manufacturer_bp.route("/email")
def receive_email():
    return make_response("All good", 200)