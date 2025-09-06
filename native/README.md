# Native Mojo Kernels (pybind11) – Vorbereitung

Inaktiv bis zum Build/Install; beeinflusst das System nicht.

## Voraussetzungen
- Python (venv empfohlen)
- CMake >= 3.18
- C++17 Toolchain (MSVC/Clang/GCC)
- pybind11 (global cmake config):
  ```bash
  pip install "pybind11[global]"
  ```

## Build (Windows PowerShell)
```powershell
cd HAK_GAL_HEXAGONAL/native/mojo_kernels
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```
Die erzeugte Extension `mojo_kernels` (z. B. `.pyd`) im Python‑Pfad verfügbar machen (z. B. per `pip install .` mit scikit‑build, oder manuell kopieren).

## Hinweis
- Erst bei `MOJO_ENABLED=true` und erfolgreichem Import wird das Modul genutzt; andernfalls greift automatisch der Python‑Fallback.
