"""
JSONL Adapter – File-based FactRepository
=========================================
Nach HAK/GAL Verfassung: nutzt die JSONL-KB als Single Source of Truth
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ports.interfaces import FactRepository
from core.domain.entities import Fact


class JsonlFactRepository(FactRepository):
    """Simple, robust JSONL-backed repository.

    Expected file format: one JSON object per line with at least key 'statement'.
    """

    def __init__(self, kb_path: str | Path = None) -> None:
        if kb_path is None:
            kb_path = Path(__file__).parent.parent.parent / 'data' / 'k_assistant.kb.jsonl'
        self.kb_path = Path(kb_path)
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)

    def _iter_facts(self):
        if not self.kb_path.exists():
            return
        with self.kb_path.open('r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                st = obj.get('statement')
                if not st:
                    continue
                context = obj.get('context') or {}
                metadata = obj.get('metadata') or {}
                yield Fact(statement=st, context=context, metadata=metadata, confidence=1.0)

    def save(self, fact: Fact) -> bool:
        try:
            with self.kb_path.open('a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'statement': fact.statement,
                    'context': fact.context,
                    'metadata': fact.metadata,
                }, ensure_ascii=False) + '\n')
            return True
        except Exception:
            return False

    def find_by_query(self, query: str, limit: int = 10) -> List[Fact]:
        out: List[Fact] = []
        q = (query or '').lower()
        for fact in self._iter_facts():
            if q in fact.statement.lower():
                out.append(fact)
                if len(out) >= limit:
                    break
        return out

    def find_all(self, limit: int = 100) -> List[Fact]:
        out: List[Fact] = []
        for fact in self._iter_facts():
            out.append(fact)
            if len(out) >= limit:
                break
        return out

    def exists(self, statement: str) -> bool:
        target = (statement or '').strip()
        if not target:
            return False
        for fact in self._iter_facts():
            if fact.statement == target:
                return True
        return False

    def count(self) -> int:
        c = 0
        for _ in self._iter_facts():
            c += 1
        return c



