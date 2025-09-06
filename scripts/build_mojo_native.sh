#!/usr/bin/env bash
set -euo pipefail

CONFIG="${1:-Release}"

echo "[BUILD] mojo_kernels (${CONFIG})"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NATIVE="${ROOT}/native/mojo_kernels"

mkdir -p "${NATIVE}/build"
cd "${NATIVE}/build"
cmake -S .. -B . -DCMAKE_BUILD_TYPE="${CONFIG}"
cmake --build . --config "${CONFIG}" --target mojo_kernels -j "$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)"

echo "[OK] Build completed"
#!/usr/bin/env bash
set -euo pipefail
CONFIG=${1:-Release}
cd "$(dirname "$0")/../native/mojo_kernels"

if ! command -v cmake >/dev/null 2>&1; then
  echo "cmake not found. Please install CMake >= 3.18" >&2
  exit 1
fi

echo "[Build] Ensuring pybind11 is available (pip install 'pybind11[global]')"

cmake -S . -B build -DCMAKE_BUILD_TYPE=${CONFIG}
cmake --build build --config ${CONFIG}

echo "[Build] Done. Output in: $(pwd)/build"
