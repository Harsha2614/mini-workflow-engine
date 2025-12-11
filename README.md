# Mini Workflow Engine (FastAPI)

This project implements a minimal workflow/graph engine inspired by LangGraph.  
It supports defining nodes, edges, shared state, branching, loops, and executing workflows using FastAPI endpoints.

---

## 🚀 Features

- Nodes as Python functions (tools)
- Shared state dictionary flowing through each node
- Sequential edges + conditional branching
- Loop support on nodes (`loop.cond`)
- Tool registry for reusable functions
- Async workflow execution
- In-memory graph and run storage
- FastAPI endpoints:
  - `POST /graph/create`
  - `POST /graph/run`
  - `GET /graph/state/{run_id}`
- Example workflow: **Code Review Mini-Agent**

---

## 📦 Project Structure

app/

├── main.py # FastAPI app + endpoints

├── engine.py # Core workflow engine

├── tools.py # Tool registry + example tools

├── workflows.py # Example workflow spec

├── models.py # Pydantic request/response models

└── README.md # Engine details

└──requirements.txt


---

## 🛠 Installation

Create a virtual environment (optional but recommended):

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows
```
# Install dependencies:
pip install -r requirements.txt

# ▶️ Running the Server

Start FastAPI with uvicorn:
uvicorn app.main:app --reload --port 8000

Open the Swagger UI:
http://127.0.0.1:8000/docs

# 🧠 Example Workflow: Code Review Mini-Agent

This rule-based workflow performs:

Extract functions

Compute complexity

Detect basic issues

Suggest improvements

Loop until quality_score ≥ threshold

Defined inside:
app/workflows.py

Automatically registered at startup.

# 🧪 Testing the Workflow

Start a run

POST /graph/run

Example request body:
```
{
  "graph_id": "code_review_v1",
  "initial_state": {
    "code": "def calculate(a, b):\n    result = a + b\n    print(result)\n    # TODO: optimize\n    return result"
  }
}


```
<img width="1365" height="722" alt="image" src="https://github.com/user-attachments/assets/892c2e45-2dde-469f-b53f-71286ff5187b" />




Response contains:
```
{ "run_id": "your-generated-run-id" }

```
<img width="1347" height="616" alt="image" src="https://github.com/user-attachments/assets/6fa49930-0b13-4fad-b112-b31303426502" />


# Poll run state

GET /graph/state/{run_id} 
<img width="1365" height="631" alt="image" src="https://github.com/user-attachments/assets/2558a876-2eb5-40f0-9b63-15fb9c9aea41" />

<img width="1361" height="664" alt="image" src="https://github.com/user-attachments/assets/fda023bc-9230-4cc7-b513-38af07eca98b" />

<img width="1350" height="461" alt="image" src="https://github.com/user-attachments/assets/ab7fade5-41cd-48a0-9790-20f6bb95448f" />



Example output:
```

{
  "run_id": "your-genrated-run-id",
  "graph_id": "code_review_v1",
  "state": {
    "code": "def calculate(a, b):\n    result = a + b\n    print(result)\n    # TODO: optimize\n    return result",
    "functions": [
      {
        "name": "calculate",
        "body": "..."
      }
    ],
    "extracted_count": 1,
    "complexities": [
      {
        "name": "calculate",
        "score": 1
      }
    ],
    "complexity_score": 1,
    "issues": [
      {
        "type": "print_usage",
        "severity": 1,
        "msg": "print found; prefer logging"
      },
      {
        "type": "todo",
        "severity": 1,
        "msg": "TODO comments present"
      }
    ],
    "issues_count": 2,
    "quality_score": 75,
    "suggestions": [
      "Fix issues flagged by the detector."
    ]
  },
  "log": [
    "-> Executing node 'extract'",
    "event: node_started:extract",
    "state snapshot: {'code': 'def calculate(a, b):\\n    result = a + b\\n    print(result)\\n    # TODO: optimize\\n    return result', 'functions': 'list', 'extracted_count': 1}",
    "event: node_finished:extract",
    "-> Executing node 'complexity'",
    "event: node_started:complexity",
    "state snapshot: {'code': 'def calculate(a, b):\\n    result = a + b\\n    print(result)\\n    # TODO: optimize\\n    return result', 'functions': 'list', 'extracted_count': 1, 'complexities': 'list', 'complexity_score': 1}",
    "event: node_finished:complexity",
    "-> Executing node 'detect'",
    "event: node_started:detect",
    "state snapshot: {'code': 'def calculate(a, b):\\n    result = a + b\\n    print(result)\\n    # TODO: optimize\\n    return result', 'functions': 'list', 'extracted_count': 1, 'complexities': 'list', 'complexity_score': 1, 'issues': 'list', 'issues_count': 2}",
    "event: node_finished:detect",
    "-> Executing node 'suggest'",
    "event: node_started:suggest",
    "state snapshot: {'code': 'def calculate(a, b):\\n    result = a + b\\n    print(result)\\n    # TODO: optimize\\n    return result', 'functions': 'list', 'extracted_count': 1, 'complexities': 'list', 'complexity_score': 1, 'issues': 'list', 'issues_count': 2, 'quality_score': 75, 'suggestions': 'list'}",
    "event: node_finished:suggest",
    "Looping on node 'suggest' (iter 1)",
    "-> Executing node 'suggest'",
    "event: node_started:suggest",
    "state snapshot: {'code': 'def calculate(a, b):\\n    result = a + b\\n    print(result)\\n    # TODO: optimize\\n    return result', 'functions': 'list', 'extracted_count': 1, 'complexities': 'list', 'complexity_score': 1, 'issues': 'list', 'issues_count': 2, 'quality_score': 75, 'suggestions': 'list'}",
    "event: node_finished:suggest",
    "Looping on node 'suggest' (iter 2)",
    "-> Executing node 'suggest'",
    "event: node_started:suggest",
    "state snapshot: {'code': 'def calculate(a, b):\\n    result = a + b\\n    print(result)\\n    # TODO: optimize\\n    return result', 'functions': 'list', 'extracted_count': 1, 'complexities': 'list', 'complexity_score': 1, 'issues': 'list', 'issues_count': 2, 'quality_score': 75, 'suggestions': 'list'}",
    "event: node_finished:suggest",
    "Looping on node 'suggest' (iter 3)",
    "-> Executing node 'suggest'",
    "event: node_started:suggest",
    "state snapshot: {'code': 'def calculate(a, b):\\n    result = a + b\\n    print(result)\\n    # TODO: optimize\\n    return result', 'functions': 'list', 'extracted_count': 1, 'complexities': 'list', 'complexity_score': 1, 'issues': 'list', 'issues_count': 2, 'quality_score': 75, 'suggestions': 'list'}",
    "event: node_finished:suggest",
    "Looping on node 'suggest' (iter 4)",
    "-> Executing node 'suggest'",
    "event: node_started:suggest",
    "state snapshot: {'code': 'def calculate(a, b):\\n    result = a + b\\n    print(result)\\n    # TODO: optimize\\n    return result', 'functions': 'list', 'extracted_count': 1, 'complexities': 'list', 'complexity_score': 1, 'issues': 'list', 'issues_count': 2, 'quality_score': 75, 'suggestions': 'list'}",
    "event: node_finished:suggest",
    "Looping on node 'suggest' (iter 5)",
    "-> Executing node 'suggest'",
    "event: node_started:suggest",
    "state snapshot: {'code': 'def calculate(a, b):\\n    result = a + b\\n    print(result)\\n    # TODO: optimize\\n    return result', 'functions': 'list', 'extracted_count': 1, 'complexities': 'list', 'complexity_score': 1, 'issues': 'list', 'issues_count': 2, 'quality_score': 75, 'suggestions': 'list'}",
    "event: node_finished:suggest",
    "Loop max_iters reached for node 'suggest'",
    "No outgoing edge for node 'suggest'. Stopping.",
    "event: done"
  ],
  "status": "finished",
  "started_at": 1765473544.8836894,
  "finished_at": 1765473545.442809
}
```



# 🧰 Engine Capabilities

Register synchronous or async tools

JSON-based graph specification

Conditions evaluated on state for branching

Looping using loop.cond and max_iters

Async background execution using asyncio

Optional WebSocket log streaming

#📈 What I Would Improve With More Time

Replace eval() with a sandboxed expression evaluator

Persist workflows and runs in SQLite/Postgres

Add authentication and multi-user isolation

Add parallel nodes & join mechanisms

Add retry logic and more detailed execution traces

Improve logging and tracing middleware

Add unit tests and GitHub Actions CI

#✨ Why This Architecture Is Clean

Engine, tools, API, and workflow definitions are separated clearly

JSON graph format makes workflows easy to modify

Tools remain pure functions (easy to test)

Supports branching, looping, state transitions cleanly

Async executor prevents blocking the server


Developed by 

# Narayana Harsha Vardhan
# 22BCE20480
# VIT AP CSE UnderGraduate

