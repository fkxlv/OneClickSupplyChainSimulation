import os
import json
from pathlib import Path
import google.generativeai as genai
from backend.schemas.planner import PlannerOutputSchema
from dotenv import load_dotenv

# 1. Загружаем переменные окружения
load_dotenv()
api_key = " " #API NEEDED

genai.configure(api_key=api_key)

def analyze_user_intent(user_intent: str, request_id: str) -> dict:
    # Используем модель, которая точно есть в твоем списке
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    prompt = f"""
    You are an expert Supply Chain Planner AI. Parse User Intent into JSON.
    USER INTENT: "{user_intent}"
    REQUEST ID: "{request_id}"

    Output EXACTLY this JSON:
    {{
        "request_id": "{request_id}",
        "product": "string",
        "quantity": float,
        "constraints": {{"max_budget": float, "deadline_days": int, "region": "string"}},
        "heuristic": "cost" or "deadline",
        "missing_information": [],
        "checklist": ["step1", "step2"],
        "reasoning_summary": "string"
    }}
    Return ONLY JSON.
    """

    try:
        response = model.generate_content(prompt)
        
        # Очистка текста от Markdown-разметки (```json ... ```)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        return json.loads(text)

    except Exception as e:
        print(f"!!! LLM FAIL: {e}")
        # Если API выдает 429 или 404, возвращаем "умную заглушку"
        # Это позволит фронтенду работать, пока API отдыхает
        return {
            "request_id": request_id,
            "product": "iPhones" if "iPhone" in user_intent else "unknown",
            "quantity": 500.0,
            "constraints": {"region": "Berlin", "max_budget": 2000.0},
            "heuristic": "cost",
            "missing_information": [],
            "checklist": ["Verify stock", "Arrange shipping to Berlin", "Finalize budget"],
            "reasoning_summary": f"Fallback mode active. (Original Error: {str(e)[:50]})"
        }
