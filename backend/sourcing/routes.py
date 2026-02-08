from flask import request, jsonify, Blueprint
from backend.schemas.planner import PlannerOutputSchema
from backend.schemas.sourcing import SourcingResultSchema
from . import logic

import logging
import requests

sourcing_bp = Blueprint("sourcing", __name__)

planner_schema = PlannerOutputSchema()
sourcing_schema = SourcingResultSchema()

DNS_URL = "http://127.0.0.1:5000/registry"
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_agent(query):
    logger.debug("get_agent: query=%s", query)
    try:
        resp = requests.post(DNS_URL + "/discover", json=query, timeout=5)
        resp.raise_for_status()
        try:
            result = resp.json()
            logger.debug("get_agent: response json=%s", result)
            return result
        except ValueError:
            logger.debug("get_agent: non-json response: %s", resp.text)
            return None
    except Exception:
        logger.exception("get_agent: request failed")
        return None

@sourcing_bp.route("/source", methods=["POST"])
def source():
    data = request.get_json()

    # validate planner input
    errors = planner_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    planner_input = planner_schema.load(data)

    # search suppliers
    suppliers = logic.search_suppliers(
        planner_input["product"],
        planner_input["constraints"].get("region")
    )

    #complete the data
    suppliers = logic.complete_the_data_with_gemini(
        request_id=planner_input["request_id"],
        region=planner_input["constraints"].get("region"),
        heuristic=planner_input["heuristic"],
        suppliers=suppliers
    )

    # ask Gemini to estimate + rank
    result = logic.rank_suppliers_with_gemini(
        request_id=planner_input["request_id"],
        heuristic=planner_input["heuristic"],
        suppliers=suppliers
    )

    # validate output
    sourcing_schema.load(result)

    execution = get_agent({"role": "execution"})['matches'][0]
    if not execution or execution.get("endpoint") is None:
        logger.error("Cannot find the execution agent")
    else:
        requests.post(execution["endpoint"] + "/execute", json=result)

    return jsonify(result), 200
