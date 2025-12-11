import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
from .engine import GraphEngine
from .tools import extract_functions, check_complexity, detect_basic_issues, suggest_improvements
from .workflows import CODE_REVIEW_GRAPH
from .models import CreateGraphRequest, CreateGraphResponse, RunGraphRequest, RunGraphResponse, RunStateResponse

app = FastAPI(title="Mini Workflow Engine")

engine = GraphEngine()

engine.register_tool("extract_functions", extract_functions)
engine.register_tool("check_complexity", check_complexity)
engine.register_tool("detect_basic_issues", detect_basic_issues)
engine.register_tool("suggest_improvements", suggest_improvements)

engine.create_graph(CODE_REVIEW_GRAPH)

@app.post("/graph/create", response_model=CreateGraphResponse)
async def create_graph(req: CreateGraphRequest):
    gid = engine.create_graph(req.graph)
    return CreateGraphResponse(graph_id=gid)

@app.post("/graph/run", response_model=RunGraphResponse)
async def run_graph(req: RunGraphRequest, background_tasks: BackgroundTasks):
    if req.graph_id not in engine.graphs:
        raise HTTPException(status_code=404, detail="Graph not found")
    run_id = await engine.run_graph(req.graph_id, req.initial_state or {}, run_async=True)
    return RunGraphResponse(run_id=run_id)

@app.get("/graph/state/{run_id}", response_model=RunStateResponse)
async def get_run_state(run_id: str):
    run = engine.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunStateResponse(
        run_id=run_id,
        graph_id=run["graph_id"],
        state=run["state"],
        log=run["log"],
        status=run["status"],
        started_at=run["started_at"],
        finished_at=run["finished_at"],
    )

@app.websocket("/ws/{run_id}")
async def websocket_run_log(websocket: WebSocket, run_id: str):
    await websocket.accept()
    loop = __import__("asyncio").get_event_loop()
    queue = []

    def listener(msg: str):
        queue.append(msg)

    engine.subscribe(run_id, listener)
    try:
        run = engine.get_run(run_id)
        if run:
            await websocket.send_json({"type": "initial", "log": run["log"], "state": run["state"], "status": run["status"]})
        while True:
            while queue:
                msg = queue.pop(0)
                await websocket.send_json({"type": "event", "message": msg, "state": engine.get_run(run_id)["state"]})
            await __import__("asyncio").sleep(0.2)
    except WebSocketDisconnect:
        engine.unsubscribe(run_id, listener)
