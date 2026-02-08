import logging
from flask import Blueprint, request

execution_bp = Blueprint("execution", __name__)

logger = logging.getLogger(__name__)

@execution_bp.route("/execute", methods=["GET", "POST"])
def execute():
    data = request.get_json() or request.args
    logger.info("execute: agent is receiving data and starting the process. data=%s", data)
    return "execution"

@execution_bp.route("/negotiation-failed", methods=["GET", "POST"])
def negotiation_failed():
    data = request.get_json() or request.args
    logger.warning("negotiation_failed: contract negotiation failed. context=%s", data)
    return "negotiation-failed"

@execution_bp.route("/verification-failed", methods=["GET", "POST"])
def verification_failed():
    data = request.get_json() or request.args
    logger.warning("verification_failed: purchased supply not verified by planner. context=%s", data)
    logger.info("verification_failed: requesting new supplier from sourcing agent")
    # TODO: call sourcing agent for new supplier
    return "verification from planner failed"