from flask import request, Blueprint, make_response

manufacturer_bp = Blueprint("manufacturer", __name__)

import random
responses = [200, 400, 400]
random.shuffle(responses)

@manufacturer_bp.route("/email")
def receive_email():
    return make_response("All good", responses.pop())