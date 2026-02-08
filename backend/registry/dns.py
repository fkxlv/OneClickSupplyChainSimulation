import json
import os
from flask import Blueprint, jsonify, request, current_app

registry_bp = Blueprint("registry", __name__)

# In-memory store (hackathon simple)
AGENTS = []


def load_agents_from_file(path: str):
    global AGENTS
    if not os.path.exists(path):
        AGENTS = []
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    AGENTS = data.get("agents", [])


def matches_query(agent: dict, query: dict) -> bool:
    # role filter
    if "role" in query and query["role"]:
        if agent.get("role") != query["role"]:
            return False

    # capabilities filter (must include all)
    if "capabilities" in query and query["capabilities"]:
        agent_caps = set(agent.get("capabilities", []))
        required_caps = set(query["capabilities"])
        if not required_caps.issubset(agent_caps):
            return False

    return True


@registry_bp.route("/agents", methods=["GET"])
def list_agents():
    return jsonify({"agents": AGENTS})


@registry_bp.route("/discover", methods=["POST"])
def discover_agents():
    query = request.get_json(force=True) or {}

    matches = [a for a in AGENTS if matches_query(a, query)]

    return jsonify({
        "query": query,
        "matches": matches,
        "count": len(matches)
    })


@registry_bp.route("/register", methods=["POST"])
def register_agent():
    agent = request.get_json(force=True)

    # Minimal validation
    required = ["agent_id", "role", "capabilities", "endpoint"]
    missing = [k for k in required if k not in agent]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Replace if same agent_id exists
    global AGENTS
    AGENTS = [a for a in AGENTS if a.get("agent_id") != agent["agent_id"]]
    AGENTS.append(agent)

    return jsonify({"status": "registered", "agent": agent})


@registry_bp.route("/reload", methods=["POST"])
def reload_agents():
    # reload agents.json without restarting service
    path = current_app.config.get("AGENTS_JSON_PATH")
    load_agents_from_file(path)
    return jsonify({"status": "reloaded", "count": len(AGENTS)})