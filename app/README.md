# Mini Workflow Engine (FastAPI)

## Overview
A minimal workflow/graph engine in Python with:
- nodes as Python tools (functions)
- a shared `state` dict that flows through nodes
- edges for sequential and conditional routing
- simple looping support
- in-memory graphs & runs
- FastAPI endpoints:
  - POST /graph/create -> create a graph
  - POST /graph/run -> start a run (async)
  - GET /graph/state/{run_id} -> query run state/log
- optional WebSocket `/ws/{run_id}` to stream events

An example graph `code_review_v1` (Code Review Mini-Agent) is registered on startup.

## Run locally
1. Create a Python venv and install requirements:
python -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]" pydantic
2. From project root run:
uvicorn app.main:app --reload --port 8000
3. Open docs: http://127.0.0.1:8000/docs

## Example usage (curl)
Start a run using the pre-registered `code_review_v1`:
curl -X POST "http://127.0.0.1:8000/graph/run
" -H "Content-Type: application/json" -d '{
"graph_id": "code_review_v1",
"initial_state": {"code": "def foo():\n print(1)\n# TODO: fix this"}
}'
Response contains `run_id`. Poll:
curl "http://127.0.0.1:8000/graph/state/
<run_id>"

## What this supports
- registering synchronous or asynchronous tools
- simple python-expression conditions for branching and loops (expressions operate on `state`, e.g. `state.get("issues_count",0) > 0`)
- per-node loops with `loop.cond` and `loop.max_iters`
- background async execution (non-blocking run start)
- WebSocket for streaming log events (optional)

## What to improve (if more time)
- Replace `eval` usage with a safe expression evaluator (e.g., `asteval` or `asteval`-like sandbox) or a domain-specific condition language
- Persist graphs and runs to a DB (SQLite or Postgres) instead of in-memory dicts
- Add authentication + user isolation for graphs & runs
- Better tooling for writing node code (e.g., pack nodes/modules, versioning)
- Enhance the edge language to support complex DAGs (parallel executions, join/sync nodes)
- Instrumentation/metrics and richer logs
Quick notes & clarifications (design decisions)

Graph spec: kept simple and JSON-friendly: nodes keyed by name, each node has tool, params, optional loop; edges map node -> next node or conditional list. See workflows.py.

Condition evaluation: expressions are Python strings evaluated with eval but with a restricted environment exposing only state. This is enough for the assignment but replace with a safe evaluator before production.

Tools: are plain Python functions (sync or async) that accept (state, params) and return a dict of updates which are merged into state.

Looping: per-node loop has cond (python-expr using state), max_iters, and optional delay.

Async: long-running or blocking tools will be executed in threadpool via run_in_executor to avoid blocking event loop.

Storage: in-memory dicts for graphs & runs for simplicity.
Example run (what to expect)

POST to /graph/run with graph_id: "code_review_v1" and initial_state: {"code": "def f():\\n print(1)\\n# TODO"}

You get run_id. Poll /graph/state/{run_id} periodically. The log will show node execution events and the state will contain:
{
  "functions": [...],
  "extracted_count": 1,
  "complexities": [...],
  "complexity_score": X,
  "issues": [...],
  "issues_count": Y,
  "quality_score": Z,
  "suggestions": [...]
}
When quality_score >= threshold the node loop ends and run status becomes finished.