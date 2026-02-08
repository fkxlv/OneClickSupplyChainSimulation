from flask import request, jsonify
from shared.schemas.planner import PlannerOutputSchema

schema = PlannerOutputSchema()

@app.route("/plan", methods=["POST"])
def plan():
    data = request.get_json()
    errors = schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    validated = schema.load(data)
    return jsonify(validated), 200
