"""
Mojo Kernels Adapter (Feature-flagged, safe by default)
=======================================================

Ziel:
- Bereitstellen einer optionalen Schnittstelle zu nativen Mojo-Kerneln
- Standardmäßig deaktiviert (MOJO_ENABLED != true)
- Fällt immer sicher auf Python-Implementierungen zurück

Hinweis:
- Dieses Modul verändert kein bestehendes Verhalten, solange das Flag nicht aktiv ist
"""

from __future__ import annotations

import os
import re
from typing import List, Tuple


def _env_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


class MojoKernelsAdapter:
    """Feature‑flagged Loader und Wrapper für optionale Mojo‑Kernels.

    - Lädt best‑effort ein pybind11/ctypes‑Modul (z. B. mojo_kernels)
    - Wenn nicht verfügbar: markiert sich als unavailable und nutzt Python‑Fallbacks
    - Bietet sichere Batch‑APIs für Parser/Validator und Duplikaterkennung
    """

    def __init__(self) -> None:
        self.flag_enabled: bool = _env_truthy(os.environ.get("MOJO_ENABLED"))
        self._backend = None
        self._load_backend_best_effort()

    # -------------------------
    # Public Introspection APIs
    # -------------------------
    def is_flag_enabled(self) -> bool:
        return self.flag_enabled

    def is_available(self) -> bool:
        return bool(self._backend)

    def backend_name(self) -> str:
        if self._backend is None:
            return "python_fallback"
        return getattr(self._backend, "__name__", "mojo_native")

    # -------------------------
    # Optional Acceleration APIs
    # -------------------------
    def validate_facts_batch(self, statements: List[str]) -> List[bool]:
        """Validiert eine Liste von Fakt‑Statements.

        Verhalten:
        - Wenn Flag aus oder Backend fehlt → Python‑Regex (identisch zum aktuellen Server‑Regex)
        - Wenn Backend vorhanden → ruft native Funktion auf, fällt bei Fehlern auf Python‑Regex zurück
        """
        # Feingranularer Gate für Validate (default: aus)
        validate_gate = _env_truthy(os.environ.get("MOJO_VALIDATE_ENABLED"))
        if not self.flag_enabled or not self._backend or not validate_gate:
            return [self._validate_python_regex(s) for s in statements]

        try:
            # Erwarteter pybind11‑Funktionsname; defensive fallback bei Abweichungen
            func = getattr(self._backend, "validate_facts_batch", None)
            if callable(func):
                result = func(statements)
                if isinstance(result, list) and all(isinstance(x, bool) for x in result):
                    return result
        except Exception:
            pass
        # Fallback
        return [self._validate_python_regex(s) for s in statements]

    def find_duplicates(self, statements: List[str], threshold: float = 0.9) -> List[Tuple[int, int, float]]:
        """Einfache Duplikaterkennung.

        Rückgabe: Liste von (index_i, index_j, score)
        - Wenn Flag aus oder Backend fehlt → sehr konservativer Python‑Fallback (Token‑Jaccard)
        - Bei Fehlern im Backend → Python‑Fallback
        """
        # Feingranularer Gate für Dedupe (default: aus)
        dupes_gate = _env_truthy(os.environ.get("MOJO_DUPES_ENABLED"))
        if not self.flag_enabled or not self._backend or not dupes_gate:
            return self._duplicates_python_jaccard(statements, threshold)

        try:
            func = getattr(self._backend, "find_duplicates", None)
            result = func(statements, threshold) if callable(func) else None
            if isinstance(result, list):
                return result
        except Exception:
            pass
        return self._duplicates_python_jaccard(statements, threshold)

    # -------------------------
    # Internals
    # -------------------------
    def _load_backend_best_effort(self) -> None:
        if not self.flag_enabled:
            self._backend = None
            return
        # 0) Optional expliziter Modulname per ENV (z. B. mojo_kernels)
        try:
            import importlib
            env_mod = os.environ.get("MOJO_BACKEND_MODULE")
            if env_mod:
                try:
                    self._backend = importlib.import_module(env_mod)
                    return
                except Exception:
                    self._backend = None
        except Exception:
            self._backend = None
        # 1) pybind11‑Stil: import mojo_kernels (Pfad ggf. vorbereiten)
        try:
            import sys
            from pathlib import Path
            # Versuche Standard-Build-Verzeichnisse zum sys.path hinzuzufügen (Windows/Linux)
            try:
                project_root = Path(__file__).resolve().parents[2]
                candidates = [
                    project_root / 'native' / 'mojo_kernels' / 'build' / 'Release',
                    project_root / 'native' / 'mojo_kernels' / 'build' / 'x64' / 'Release',
                    project_root / 'native' / 'mojo_kernels' / 'build'
                ]
                for p in candidates:
                    if p.exists():
                        sp = str(p)
                        if sp not in sys.path:
                            sys.path.insert(0, sp)
            except Exception:
                pass
            import importlib
            try:
                self._backend = importlib.import_module('mojo_kernels')
                return
            except Exception:
                # 1b) Versuche vollqualifizierten Pfad, falls PYTHONPATH auf Projektwurzel zeigt
                try:
                    self._backend = importlib.import_module('src_hexagonal.mojo_kernels')
                    return
                except Exception:
                    self._backend = None
        except Exception:
            self._backend = None
        # 2) ctypes/cffi – optional: hier bewusst nicht implementiert, um Abhängigkeiten zu vermeiden
        #    Bei Bedarf kann hier ein Loader ergänzt werden, der native/libhakgal_mojo.* lädt

    @staticmethod
    def _validate_python_regex(statement: str) -> bool:
        pattern = r"^[A-Za-z_][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.\s*$"
        return bool(re.match(pattern, statement or ""))

    @staticmethod
    def _duplicates_python_jaccard(statements: List[str], threshold: float) -> List[Tuple[int, int, float]]:
        def tokens(s: str) -> set:
            return set(re.findall(r"[A-Za-z0-9_]+", s.lower()))

        tok = [tokens(s or "") for s in statements]
        n = len(tok)
        results: List[Tuple[int, int, float]] = []
        for i in range(n):
            ti = tok[i]
            if not ti:
                continue
            for j in range(i + 1, n):
                tj = tok[j]
                if not tj:
                    continue
                inter = len(ti & tj)
                union = len(ti | tj) or 1
                score = inter / union
                if score >= max(0.0, min(1.0, threshold)):
                    results.append((i, j, float(score)))
        return results


__all__ = [
    "MojoKernelsAdapter",
]


