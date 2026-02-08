from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import uuid

# Импортируем нашу логику и схему
from planner.logic import analyze_user_intent
from shared.schemas.planner import PlannerOutputSchema

# Создаем Blueprint вместо app, чтобы подключить его в __init__.py
bp = Blueprint('planner', __name__)

output_schema = PlannerOutputSchema()

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