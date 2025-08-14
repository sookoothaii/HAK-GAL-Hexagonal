from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone


@dataclass
class KillSwitchState:
    mode: str  # 'normal' | 'safe'
    reason: str
    by: str
    updated_at: str


class KillSwitch:
    """
    Minimal-invasiver Kill-Switch für die Hex-Suite.
    - Persistiert Zustand in JSON (projektweit), überlebt Neustarts
    - 'safe'-Modus drosselt/unterbindet riskante Pfade
    - Standard ist 'normal'
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.state_path = self.project_root / 'kill_switch_state.json'
        self._state = self._load() or KillSwitchState(
            mode='normal',
            reason='initial',
            by='system',
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

    def _load(self) -> Optional[KillSwitchState]:
        try:
            if self.state_path.exists():
                data = json.loads(self.state_path.read_text(encoding='utf-8', errors='ignore'))
                return KillSwitchState(**data)
        except Exception:
            return None
        return None

    def _save(self) -> None:
        try:
            self.state_path.write_text(
                json.dumps(asdict(self._state), ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
        except Exception:
            pass

    def state(self) -> Dict[str, Any]:
        return asdict(self._state)

    def is_safe(self) -> bool:
        return self._state.mode.lower() == 'safe'

    def activate_safe(self, reason: str, by: str = 'operator') -> Dict[str, Any]:
        self._state = KillSwitchState(
            mode='safe',
            reason=reason or 'unspecified',
            by=by,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        self._save()
        return self.state()

    def deactivate(self, by: str = 'operator') -> Dict[str, Any]:
        self._state = KillSwitchState(
            mode='normal',
            reason='deactivated',
            by=by,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        self._save()
        return self.state()




