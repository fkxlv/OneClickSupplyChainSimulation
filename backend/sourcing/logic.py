import os
import json
import requests
#import google.genai as genai
import google.generativeai as genai
from backend.schemas.sourcing import SourcingResultSchema

# Configure Gemini
#genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
genai.configure(api_key="AIzaSyCq2h7jVlCvGwdSH627MV7ChrYZ6GinBSc")
model = genai.GenerativeModel("gemini-1.5-flash")

SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")


def search_suppliers(product: str, region: str) -> list[dict]:
    """
    Searches suppliers using SerpAPI and returns a simple list.
    """
    params = {
        "q": f"{product} supplier manufacturer {region}",
        "engine": "google",
        "api_key": SERPAPI_API_KEY,
        "num": 7
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
            "capabilities": [product],
            "base_unit_cost": 0,
            "base_lead_time_days": 0,
            "min_total_price": 0,
            "max_total_price":0,
            max_lead_time_delays:0,
        })

    return suppliers

def complete_the_data_with_gemini(
    request_id: str,
    region: str,
    heuristic: str,
    suppliers: list[dict]
    ) -> list[dict]:

    model = genai.GenerativeModel("gemini-1.5-pro")

    prompt = f"""
        You are a sourcing expert.

        Request ID: {request_id}
        Product: {product}
        Region: {region}

        Given the supplier list below, infer and fill in missing fields:
        - base_unit_cost (float)
        - base_lead_time_days (int)
        - min_total_price (float)
        - max_total_price (float)
        - max_lead_time_days (int)

        Use realistic market estimates for the region and product.
        Return ONLY valid JSON with the same list structure.

        Suppliers:
        {json.dumps(suppliers, indent=2)}
        """

    response = model.generate_content(prompt)

    return json.loads(response.text)



def rank_suppliers_with_gemini(
    request_id: str,
    heuristic: str,
    suppliers: list[dict]
) -> dict:
    """
    Uses Gemini to rank suppliers by optimality.
    Index 0 = most optimal.
    """

    if heuristic not in {"cost", "deadline"}:
        raise ValueError("heuristic must be 'cost' or 'deadline'")

    model = genai.GenerativeModel("gemini-1.5-pro")

    prompt = f"""
        You are a sourcing optimization engine.

        Heuristic:
        - "cost": prioritize lowest total price, then lead time
        - "deadline": prioritize shortest lead time, then cost

        Task:
        Reorder the suppliers from most optimal (index 0) to least optimal based on heuristic.
        Do NOT modify supplier fields.
        Do NOT add or remove suppliers.
        Return ONLY valid JSON.

Suppliers:
{json.dumps(suppliers, indent=2)}
"""

    response = model.generate_content(prompt)

    ranked_suppliers = json.loads(response.text)

    return {
        "request_id": request_id,
        "heuristic": heuristic,
        "ranked_suppliers": ranked_suppliers,
        "notes": f"Ranking inferred by Gemini using '{heuristic}' heuristic"
    }




def estimate_and_rank_with_gemini(
    request_id: str,
    heuristic: str,
    suppliers: list[dict]
) -> dict:
    """
    Sends suppliers to Gemini and asks it to estimate values
    and return a valid SourcingResultSchema JSON.
    """
    prompt = f"""
    You are a Supply Chain Sourcing AI.

    Given the suppliers below, estimate:
    - base_unit_cost
    - base_lead_time_days
    - min_total_price
    - max_total_price
    - max_lead_time_days

    Then rank suppliers based on heuristic: "{heuristic}"

    Suppliers:
    {json.dumps(suppliers, indent=2)}

    Return ONLY valid JSON in this exact format:
    {{
        "request_id": "{request_id}",
        "heuristic": "{heuristic}",
        "ranked_suppliers": [
            {{
                "supplier_id": "string",
                "name": "string",
                "region": "string",
                "capabilities": ["string"],
                "base_unit_cost": float,
                "base_lead_time_days": int,
                "min_total_price": float,
                "max_total_price": float,
                "max_lead_time_days": int
            }}
        ],
        "notes": "string"
    }}
    """

    response = model.generate_content(prompt)
    cleaned = response.text.replace("```json", "").replace("```", "").strip()
    parsed = json.loads(cleaned)

    # Validate schema
    SourcingResultSchema().load(parsed)
    return parsed

"""
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
    heuristic: str,
    product: str,
    region: str
) -> List[Dict]:

    prompt = {
        "heuristic": heuristic,
        "suppliers": suppliers
    }

    response = gemini.generate_content(
        fYou are an expert Supply Chain Analytics AI.
        Your goal is to rank the suppliers based on who is the most optimal one.
        The product is {product}. You are ordering from region {region}. 
        Consider the logistics price: consider the purchase region and the region of the supplier.
        Rank the suppliers based on the given heuristic ({heuristic}).
        Given suppliers are {suppliers}
        You must output a valid JSON object that lists suppliers matching this structure EXACTLY:
        {
            "supplier_id": "https://abc-fasteners.de",
            "name": "ABC Fasteners GmbH",
            "region": "Germany",
            "capabilities": ["steel bolts"],
            "base_unit_cost": 4.2,
            "base_lead_time_days": 9,
            "min_total_price": 4700,
            "max_total_price": 5200,
            "max_lead_time_days": 14
}
        
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
    return result"""
