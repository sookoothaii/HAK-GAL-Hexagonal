from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class AuditLogger:
    """
    Lightweight append-only JSONL audit logger with hash chaining.
    Stored at project_root / 'audit_log.jsonl'.
    """

    def __init__(self, project_root: Optional[Path] = None, filename: str = 'audit_log.jsonl') -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.path = self.project_root / filename
        self._last_hash = None
        try:
            if self.path.exists():
                # load last line to continue chain
                last = None
                with self.path.open('rb') as f:
                    f.seek(0, 2)
                    end = f.tell()
                    step = 1024
                    chunk = b''
                    while end > 0 and not last:
                        read = max(0, end - step)
                        f.seek(read)
                        chunk = f.read(end - read) + chunk
                        end = read
                        lines = chunk.splitlines()
                        if lines:
                            last_line = lines[-1]
                            try:
                                obj = json.loads(last_line.decode('utf-8', errors='ignore'))
                                last = obj
                            except Exception:
                                continue
                if last and isinstance(last, dict):
                    self._last_hash = last.get('entry_hash')
        except Exception:
            self._last_hash = None

    def _compute_hash(self, data: Dict[str, Any]) -> str:
        payload = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
        return hashlib.sha256(payload).hexdigest()

    def log(self, event: str, payload: Dict[str, Any]) -> None:
        try:
            entry = {
                'ts': datetime.now(timezone.utc).isoformat(),
                'event': event,
                'payload': payload,
                'prev_hash': self._last_hash,
            }
            entry_hash = self._compute_hash(entry)
            entry['entry_hash'] = entry_hash
            line = json.dumps(entry, ensure_ascii=False)
            with self.path.open('a', encoding='utf-8') as f:
                f.write(line + '\n')
            self._last_hash = entry_hash
        except Exception:
            pass





























