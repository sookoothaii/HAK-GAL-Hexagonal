# Build Guide – Native mojo_kernels (pybind11)

Ziel: Vorbereiten des nativen Moduls ohne Systemeinbindung. Aktiv wird es erst mit Flag+Install.

## Voraussetzungen
- Python (venv empfohlen)
- CMake >= 3.18
- C++17 Toolchain (MSVC/Clang/GCC)
- `pip install "pybind11[global]"`

## Windows (PowerShell)
```powershell
.\scripts uild_mojo_native.ps1 -Config Release
```

## Linux/Mac (Bash)
```bash
bash ./HAK_GAL_HEXAGONAL/scripts/build_mojo_native.sh Release
```

## Installation (optional, später)
- Per scikit-build-core/setuptools oder manuelles Platzieren der erzeugten `.pyd`/`.so` in den Python‑Pfad.
- Erst nach Installation und Setzen von `MOJO_ENABLED=true` wird das Modul vom Adapter geladen.

## Verifikation
```powershell
$env:MOJO_ENABLED="true"
$env:PYTHONPATH="D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal;$env:PYTHONPATH"
python -c "import mojo_kernels as m; print(m.validate_facts_batch(['HasPart(A,B).']))"
```

## Sicherheit
- Keine Änderungen am laufenden System; alle Schritte sind offline.
