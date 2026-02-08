from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import uuid

import logging
import requests

# Импортируем нашу логику и схему
from .logic import analyze_user_intent
from backend.schemas.planner import PlannerOutputSchema

# Создаем Blueprint вместо app, чтобы подключить его в __init__.py
bp = Blueprint('planner', __name__)

output_schema = PlannerOutputSchema()

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


@bp.route("/plan", methods=["POST"])
def generate_plan():
    """
    Принимает {"intent": "Need 50 drones..."}
    Возвращает валидный PlannerOutputSchema JSON
    """
    data = request.get_json()
    
    if not data or "intent" not in data:
        return jsonify({"error": "Field 'intent' is required"}), 400

    user_intent = data["intent"]
    # Генерируем ID запроса, если его нет
    req_id = data.get("request_id", str(uuid.uuid4()))

    print(f"PLANNER: Analyzing intent -> {user_intent}")

    # 1. Запускаем логику (LLM)
    raw_result = analyze_user_intent(user_intent, req_id)

    # 2. Валидируем ответ через Marshmallow
    try:
        # load проверит типы данных и обязательные поля
        validated_data = output_schema.load(raw_result)
        
        sourcing = get_agent({"role": "sourcing"})['matches'][0]
        if not sourcing or sourcing.get("endpoint") is None:
            logger.error("Cannot find the sourcing agent")
        else:
            request.post(sourcing["endpoint"] + "/source", json=validated_data)

        # Если всё ок, возвращаем результат
        return jsonify(validated_data), 200

    except ValidationError as err:
        # Если LLM вернула кривой JSON, который не подходит под схему
        print("Validation Error:", err.messages)
        return jsonify({
            "error": "LLM output schema validation failed",
            "details": err.messages,
            "raw_output": raw_result
        }), 500