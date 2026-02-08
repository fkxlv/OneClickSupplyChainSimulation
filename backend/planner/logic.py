import os
import json
from pathlib import Path
import google.generativeai as genai
from shared.schemas.planner import PlannerOutputSchema
from dotenv import load_dotenv  # <--- 1. Импортируем загрузчик

# 2. Загружаем переменные из файла .env в память
load_dotenv()
env_path = Path(__file__).parent.parent / '.env.example' 
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ ОШИБКА: Не найден GEMINI_API_KEY в файле .env")

genai.configure(api_key=api_key)
# Настройка Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def analyze_user_intent(user_intent: str, request_id: str) -> dict:
    """
    Отправляет запрос в LLM и возвращает словарь, валидный по PlannerOutputSchema.
    """
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')

    # Получаем строковое описание схемы, чтобы LLM знала, в каком формате отвечать
    schema_structure = json.dumps(PlannerOutputSchema().fields, default=str) 
    
    # Системный промпт
    prompt = f"""
    You are an expert Supply Chain Planner AI. 
    Your goal is to parse the User Intent into a structured extraction plan.

    USER INTENT: "{user_intent}"
    REQUEST ID: "{request_id}"

    You must output a valid JSON object matching this structure EXACTLY:
    {{
        "request_id": "{request_id}",
        "product": "string (name of item)",
        "quantity": float,
        "constraints": {{
            "max_budget": float or null,
            "deadline_days": int or null,
            "region": "string or null"
        }},
        "heuristic": "cost" or "deadline" (choose based on intent, default to cost),
        "missing_information": [list of strings if anything is unclear],
        "checklist": [list of strings, step-by-step plan for sourcing this item],
        "reasoning_summary": "string explaining your decision"
    }}

    If the user does not specify a quantity, try to infer it or set 1 if impossible.
    Return ONLY the JSON. No markdown formatting.
    """

    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        parsed_json = json.loads(cleaned_text)
        
        return parsed_json
    except Exception as e:
        print(f"LLM Error: {e}")
        # Возвращаем структуру ошибки, если LLM сломалась
        return {
            "request_id": request_id,
            "product": "unknown",
            "quantity": 1,
            "constraints": {},
            "heuristic": "cost",
            "missing_information": ["Failed to parse intent"],
            "checklist": ["Error"],
            "reasoning_summary": str(e)
        }