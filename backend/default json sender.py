import requests

response = requests.post(
    "http://localhost:5000/sourcing",
    json={
  "status": "needs_more_info",
  "planner_output": {
    "request_id": "req_123",
    "product": "laptop",
    "quantity": 1,
    "constraints": {
      "max_budget": None,
      "deadline_days": None,
      "region": None
    },
    "heuristic": "deadline",
    "missing_information": [
      "target_specs",
      "preferred_brand"
    ],
    "checklist": [
      "Clarify required specs (RAM/CPU/storage)",
      "Clarify preferred brand or OS",
      "Search options and compare delivery times",
      "Select best match for deadline"
    ],
    "reasoning_summary": None
  }
}

)




