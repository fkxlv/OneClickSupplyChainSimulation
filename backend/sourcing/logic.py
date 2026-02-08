import os
import uuid
import requests
from typing import List, Dict

from marshmallow import ValidationError
from shared.schemas.sourcing import SupplierSchema, SourcingResultSchema
from shared.schemas.planner import PlannerOutputSchema

from google.generativeai import GenerativeModel, configure


# ========== CONFIG ==========
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

configure(api_key=GEMINI_API_KEY)
gemini = GenerativeModel("gemini-1.5-flash")


# ========== SEARCH ==========
def search_suppliers(product: str, region: str) -> List[Dict]:
    if not SERPAPI_API_KEY:
        raise RuntimeError("SERPAPI_API_KEY missing")

    params = {
        "q": f"{product} supplier manufacturer {region}",
        "engine": "google",
        "api_key": SERPAPI_API_KEY,
        "num": 5
    }

    r = requests.get("https://serpapi.com/search", params=params)
    r.raise_for_status()
    results = r.json()

    suppliers = []
    for item in results.get("organic_results", []):
        suppliers.append({
            "supplier_id": str(uuid.uuid4()),
            "name": item.get("title"),
            "region": region,
            "capabilities": [product]
        })

    return suppliers


# ========== COST & LOGISTICS ==========
def estimate_supplier_metrics(
    supplier: Dict,
    quantity: float,
    region: str
) -> Dict:
    base_unit_cost = round(3.5 + hash(supplier["name"]) % 300 / 100, 2)
    base_lead_time = 7 + hash(supplier["supplier_id"]) % 10

    logistics_cost = 500 if region else 1200
    total_price = base_unit_cost * quantity + logistics_cost

    supplier.update({
        "base_unit_cost": base_unit_cost,
        "base_lead_time_days": base_lead_time,
        "min_total_price": total_price,
        "max_total_price": total_price * 1.1,
        "max_lead_time_days": base_lead_time + 5
    })

    return supplier


# ========== GEMINI RANKING ==========
def rank_with_gemini(
    suppliers: List[Dict],
    heuristic: str
) -> List[Dict]:

    prompt = {
        "heuristic": heuristic,
        "suppliers": suppliers
    }

    response = gemini.generate_content(
        f"{prompt}\nReturn JSON only."
    )

    data = response.text.strip().replace("```json", "").replace("```", "")
    ranking_data = eval(data)  # trusted model output in hackathon context

    order = ranking_data["ranking"]
    id_map = {s["supplier_id"]: s for s in suppliers}

    return [id_map[sid] for sid in order]


# ========== MAIN ENTRY ==========
def run_sourcing(planner_json: Dict) -> Dict:
    # Validate planner input
    planner = PlannerOutputSchema().load(planner_json)

    region = planner["constraints"].get("region")
    if not region:
        return {
            "request_id": planner["request_id"],
            "heuristic": planner["heuristic"],
            "ranked_suppliers": [],
            "notes": "Region missing, cannot source suppliers."
        }

    suppliers = search_suppliers(planner["product"], region)

    enriched = [
        estimate_supplier_metrics(s, planner["quantity"], region)
        for s in suppliers
    ]

    # Filter by constraints
    filtered = []
    for s in enriched:
        if planner["constraints"].get("max_budget") and \
           s["min_total_price"] > planner["constraints"]["max_budget"]:
            continue

        if planner["constraints"].get("deadline_days") and \
           s["base_lead_time_days"] > planner["constraints"]["deadline_days"]:
            continue

        filtered.append(s)

    if not filtered:
        return {
            "request_id": planner["request_id"],
            "heuristic": planner["heuristic"],
            "ranked_suppliers": [],
            "notes": "No suppliers satisfy budget/deadline constraints."
        }

    ranked = rank_with_gemini(filtered, planner["heuristic"])

    # Validate output schema
    result = {
        "request_id": planner["request_id"],
        "heuristic": planner["heuristic"],
        "ranked_suppliers": ranked,
        "notes": "Ranked using Gemini reasoning."
    }

    SourcingResultSchema().load(result)
    return result
