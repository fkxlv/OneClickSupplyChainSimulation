from flask import request, jsonify, Blueprint
from backend.schemas.planner import PlannerOutputSchema
from backend.schemas.sourcing import SourcingResultSchema
from . import logic

sourcing_bp = Blueprint("sourcing", __name__)

planner_schema = PlannerOutputSchema()
sourcing_schema = SourcingResultSchema()


@sourcing_bp.route("/source", methods=["POST"])
def source():
    data = request.get_json()

    # validate planner input
    errors = planner_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    planner_input = planner_schema.load(data)

    # search suppliers
    suppliers = search_suppliers(
        planner_input["product"],
        planner_input["constraints"].get("region")
    )

    # ask Gemini to estimate + rank
    result = estimate_and_rank_with_gemini(
        request_id=planner_input["request_id"],
        heuristic=planner_input["heuristic"],
        suppliers=suppliers
    )

    # validate output
    sourcing_schema.load(result)

    return jsonify(result), 200
