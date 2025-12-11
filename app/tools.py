import asyncio
import math
from typing import Dict, Any



def extract_functions(state: Dict[str, Any], params: Dict[str, Any]):
    """
    Pretend to extract functions from code text in state['code'].
    Will produce state['functions'] = list of function dicts.
    """
    code = state.get("code", "")
    funcs = []
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("def "):
            name = line.split("(")[0].replace("def ", "").strip()
            funcs.append({"name": name, "body": "..."})
    if not funcs:
        funcs = [{"name": "script", "body": code[:100]}]
    return {"functions": funcs, "extracted_count": len(funcs)}

def check_complexity(state: Dict[str, Any], params: Dict[str, Any]):
    """
    Assign a complexity score per function based on heuristics (longer -> more complex).
    Adds 'complexities' list and an aggregated 'complexity_score'.
    """
    funcs = state.get("functions", [])
    complexities = []
    for f in funcs:
        body = f.get("body", "")
        score = max(1, len(body) // 20)
        complexities.append({"name": f.get("name"), "score": score})
    total = sum(c["score"] for c in complexities)
    return {"complexities": complexities, "complexity_score": total}

def detect_basic_issues(state: Dict[str, Any], params: Dict[str, Any]):
    """
    Basic lint-like checks; we create an 'issues' list and a count.
    """
    code = state.get("code", "")
    issues = []
    if "print(" in code and "logging" not in code:
        issues.append({"type": "print_usage", "severity": 1, "msg": "print found; prefer logging"})
    if "TODO" in code:
        issues.append({"type": "todo", "severity": 1, "msg": "TODO comments present"})
    if "eval(" in code:
        issues.append({"type": "dangerous_eval", "severity": 5, "msg": "use of eval"})
    return {"issues": issues, "issues_count": len(issues)}

def suggest_improvements(state: Dict[str, Any], params: Dict[str, Any]):
    """
    Create a crude quality_score and suggestions.
    """
    complexity = state.get("complexity_score", 0)
    issues = state.get("issues_count", 0)
    quality_score = max(0, 100 - (complexity * 5) - (issues * 10))
    suggestions = []
    if complexity > 10:
        suggestions.append("Consider splitting large functions into smaller ones.")
    if issues > 0:
        suggestions.append("Fix issues flagged by the detector.")
    if quality_score >= params.get("threshold", 80):
        suggestions.append("Quality meets threshold.")
    return {"quality_score": quality_score, "suggestions": suggestions}
