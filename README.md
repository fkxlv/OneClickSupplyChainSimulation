# OneClickSupplyChainSimulation
One click AI-supply chain agents NANDA-native "Internet of Agents" simulation using LangGraph-based multi-agent network

# How to run servers
The 4 Agents are running through with following commands

- Planner:
```
flask --app backend.planner run --debug --port 5001
```

- Sourcing:
```
flask --app backend.sourcing run --debug --port 5002
```

- Execution:
```
flask --app backend.execution run --debug --port 5003
```