from execution import *

# Getting all the relevant agents
payload = {
  "request_id": "req-2026-02-08-001",
  "heuristic": "cost",
  "ranked_suppliers": [
    {
      "supplier_id": "sup-001",
      "name": "Nordic Components GmbH",
      "region": "Germany",
      "capabilities": ["pcb_assembly", "plastic_injection", "quality_testing"],
      "base_unit_cost": 4.75,
      "base_lead_time_days": 10,
      "min_total_price": 4200.0,
      "max_total_price": 5800.0,
      "max_lead_time_days": 18
    },
    {
      "supplier_id": "sup-002",
      "name": "Shenzhen Rapid Manufacturing",
      "region": "China",
      "capabilities": ["pcb_assembly", "mass_production"],
      "base_unit_cost": 3.2,
      "base_lead_time_days": 14,
      "min_total_price": 3500.0,
      "max_total_price": 5200.0,
      "max_lead_time_days": 25
    },
    {
      "supplier_id": "sup-003",
      "name": "Baltic Precision Sp. z o.o.",
      "region": "Poland",
      "capabilities": ["cnc_machining", "quality_testing", "packaging"],
      "base_unit_cost": 4.1,
      "base_lead_time_days": 9,
      "min_total_price": 3900.0,
      "max_total_price": 6100.0,
      "max_lead_time_days": 16
    }
  ],
  "notes": "Ranked using cost heuristic. Suppliers filtered for capability match and acceptable lead time."
}

receive_from_sourcing(payload)