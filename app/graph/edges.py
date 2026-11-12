

def route_after_context_check(state: dict) -> str:
    """Choose the next node based on context availability."""

    if state.get("has_context", False):
        return "generate"

    return "insufficient_context"
