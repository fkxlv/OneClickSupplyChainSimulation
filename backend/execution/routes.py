import logging
from flask import Blueprint, jsonify, request
from backend.schemas.execution import ExecutionResultSchema
from backend.schemas.sourcing import SourcingResultSchema
from .execution import receive_from_sourcing
import logging
import requests

sourcing_bp = Blueprint("sourcing", __name__)

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

execution_bp = Blueprint("execution", __name__)

@execution_bp.route("/execute", methods=["POST"])
def execute():
    data = request.get_json()

    payload = sourcing_schema.dump(data)
    result = receive_from_sourcing(payload)

    logger.info("execute: agent is receiving data and starting the process. data=%s", data)
    return jsonify(result)