from __future__ import annotations

from typing import Any, Dict


def estimate_harm_prob(action: str, context: Dict[str, Any]) -> float:
    """Very lightweight heuristic. Replace with real model.
    Defaults to low risk for read-only, moderate for write.
    """
    sensitivity = context.get('sensitivity', 'write')
    if sensitivity == 'read':
        return 0.0001
    # Slightly higher for write, still under threshold by default
    return 0.0005


def estimate_sustain_index(action: str, context: Dict[str, Any]) -> float:
    """Lightweight heuristic for sustainability index [0..1]."""
    return 0.95





























