CODE_REVIEW_GRAPH = {
    "id": "code_review_v1",
    "start": "extract",
    "nodes": {
        "extract": {
            "tool": "extract_functions",
            "params": {}
        },
        "complexity": {
            "tool": "check_complexity",
            "params": {}
        },
        "detect": {
            "tool": "detect_basic_issues",
            "params": {}
        },
        "suggest": {
            "tool": "suggest_improvements",
            "params": {"threshold": 80},
           
            "loop": {
                "cond": "state.get('quality_score', 0) < 80",
                "max_iters": 5,
                "delay": 0.1
            }
        }
    },
    "edges": {
       
        "extract": "complexity",
        "complexity": "detect",
        "detect": "suggest",
        "suggest": None
    }
}#
