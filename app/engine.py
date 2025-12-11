import asyncio
import uuid
import time
from typing import Any, Callable, Dict, Optional, List

class GraphEngine:
    def __init__(self):
        self.tools: Dict[str, Callable[[Dict[str, Any], Dict[str, Any]], Any]] = {}
        self.graphs: Dict[str, Dict] = {}
        self.runs: Dict[str, Dict] = {}
        self._run_listeners: Dict[str, List[Callable[[str], None]]] = {}

    def register_tool(self, name: str, fn: Callable[[Dict, Dict], Any]):
        self.tools[name] = fn

    def create_graph(self, graph_spec: Dict) -> str:
        gid = graph_spec.get("id") or str(uuid.uuid4())
        self.graphs[gid] = graph_spec
        return gid

    async def run_graph(self, graph_id: str, initial_state: Dict, run_async: bool = True) -> str:
        if graph_id not in self.graphs:
            raise KeyError("graph not found")
        run_id = str(uuid.uuid4())
        self.runs[run_id] = {
            "graph_id": graph_id,
            "state": initial_state.copy(),
            "log": [],
            "status": "running",
            "started_at": time.time(),
            "finished_at": None,
        }
        if run_async:
            asyncio.create_task(self._execute_run(run_id))
        else:
            await self._execute_run(run_id)
        return run_id

    async def _execute_run(self, run_id: str):
        run = self.runs[run_id]
        graph = self.graphs[run["graph_id"]]
        nodes = graph.get("nodes", {})
        edges = graph.get("edges", {})
        start_node = graph.get("start")
        if not start_node:
            run["log"].append("No start node specified.")
            run["status"] = "failed"
            return
        iter_counts = {}

        current = start_node
        try:
            while current is not None:
                node_spec = nodes.get(current)
                if node_spec is None:
                    run["log"].append(f"Node '{current}' not found. Stopping.")
                    break

                run["log"].append(f"-> Executing node '{current}'")
                await self._notify_listeners(run_id, f"node_started:{current}")

                tool_name = node_spec.get("tool")
                params = node_spec.get("params", {})
                result = {}
                if tool_name:
                    tool = self.tools.get(tool_name)
                    if tool is None:
                        run["log"].append(f"Tool '{tool_name}' not registered. Skipping.")
                    else:
                        if asyncio.iscoroutinefunction(tool):
                            res = await tool(run["state"], params)
                        else:
                            loop = asyncio.get_running_loop()
                            res = await loop.run_in_executor(None, lambda: tool(run["state"], params))
                        if isinstance(res, dict):
                            run["state"].update(res)
                        else:
                            run["state"]["last_result"] = res
                run["log"].append(f"state snapshot: {self._shallow_state(run['state'])}")
                await self._notify_listeners(run_id, f"node_finished:{current}")
                loop_spec = node_spec.get("loop")
                if loop_spec:
                    cond_expr = loop_spec.get("cond") 
                    max_iters = loop_spec.get("max_iters", 50)
                    iters = iter_counts.get(current, 0)
                    iter_counts[current] = iters + 1
                    if iters < max_iters and self._eval_cond(cond_expr, run["state"]):
                        run["log"].append(f"Looping on node '{current}' (iter {iters+1})")
                        await asyncio.sleep(loop_spec.get("delay", 0))
                        continue
                    else:
                        if iters >= max_iters:
                            run["log"].append(f"Loop max_iters reached for node '{current}'")
                next_node = None
                edge_def = edges.get(current)
                if edge_def is None:
                    run["log"].append(f"No outgoing edge for node '{current}'. Stopping.")
                    next_node = None
                else:
                    if isinstance(edge_def, str):
                        next_node = edge_def
                    elif isinstance(edge_def, dict):
                        next_node = self._choose_edge(edge_def, run["state"])
                    elif isinstance(edge_def, list):
                        chosen = None
                        for e in edge_def:
                            if e.get("cond") == "default":
                                chosen = e.get("node")
                            else:
                                if self._eval_cond(e.get("cond"), run["state"]):
                                    chosen = e.get("node")
                                    break
                        next_node = chosen
                    else:
                        run["log"].append(f"Unsupported edge def for node '{current}'. Stopping.")
                        next_node = None

                current = next_node
                await asyncio.sleep(0)
            run["status"] = "finished"
        except Exception as exc:
            run["log"].append(f"execution error: {repr(exc)}")
            run["status"] = "failed"
        finally:
            run["finished_at"] = time.time()
            await self._notify_listeners(run_id, "done")

    async def _notify_listeners(self, run_id: str, message: str):
        run = self.runs.get(run_id)
        if not run:
            return
        run["log"].append(f"event: {message}")
        listeners = self._run_listeners.get(run_id, [])
        for cb in listeners:
            try:
                cb(message)
            except Exception:
                pass

    def subscribe(self, run_id: str, callback: Callable[[str], None]):
        self._run_listeners.setdefault(run_id, []).append(callback)

    def unsubscribe(self, run_id: str, callback: Callable[[str], None]):
        if run_id in self._run_listeners:
            try:
                self._run_listeners[run_id].remove(callback)
            except ValueError:
                pass

    def get_run(self, run_id: str) -> Optional[Dict]:
        return self.runs.get(run_id)

    def get_graph(self, graph_id: str) -> Optional[Dict]:
        return self.graphs.get(graph_id)

    def _shallow_state(self, state: Dict):
        return {k: (v if isinstance(v, (int, float, str, bool, type(None))) else type(v).__name__) for k, v in state.items()}

    def _eval_cond(self, cond: Optional[str], state: Dict) -> bool:
        """Evaluate a condition string using `state` safely-ish. cond may be None or empty -> False."""
        if not cond:
            return False
        try:
            allowed_globals = {"__builtins__": {}}
            allowed_locals = {"state": state}
            return bool(eval(cond, allowed_globals, allowed_locals))
        except Exception:
            return False

    def _choose_edge(self, edge_def: Dict, state: Dict):
        for case in edge_def.get("cases", []):
            if self._eval_cond(case.get("cond"), state):
                return case.get("node")
        return edge_def.get("default")#
