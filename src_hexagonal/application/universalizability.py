from __future__ import annotations

from typing import Any, Dict


def is_universalizable(action: str, context: Dict[str, Any]) -> bool:
    """Placeholder universalizability check.
    Conservative default: allow common safe operations, require proof for destructive ones.
    """
    safe_prefixes = ('read_', 'list_', 'query_', 'search_', 'status_', 'explain_')
    if any(action.startswith(p) for p in safe_prefixes):
        return True
    # For other actions, expect explicit proof flag in context
    return bool(context.get('universalizable_proof'))





























