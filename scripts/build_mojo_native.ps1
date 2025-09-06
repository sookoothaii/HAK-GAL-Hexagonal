param(
    [ValidateSet('Debug','Release')]
    [string]$Config = 'Release'
)

$ErrorActionPreference = 'Stop'

Write-Host "[BUILD] mojo_kernels ($Config)"

$root = Split-Path -Parent $PSScriptRoot
$native = Join-Path $root 'native/mojo_kernels'

Push-Location $native
try {
    if (-not (Test-Path 'build')) { New-Item -ItemType Directory -Path 'build' | Out-Null }
    Set-Location 'build'
    cmake -S .. -B . -DCMAKE_BUILD_TYPE=$Config
    cmake --build . --config $Config --target mojo_kernels -j 8
    Write-Host "[OK] Build completed"
}
finally {
    Pop-Location
}

Param(
	[string]$Config = 'Release'
)
$ErrorActionPreference = 'Stop'

# Verzeichnisse
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$here/../native/mojo_kernels"
$src = Get-Location
$build = Join-Path $src 'build'

# Python im Hex-venv
$py = "$(Split-Path $here -Parent)\.venv_hexa\Scripts\python.exe"
if (-not (Test-Path $py)) {
	throw "Python venv nicht gefunden: $py"
}

Write-Host "[Build] Ensuring pybind11 is available (pip install pybind11[global])"
& $py -m pip install 'pybind11[global]' -U | Out-Null

# pybind11 CMake-Verzeichnis ermitteln
$pb = & $py -c "import pybind11; print(pybind11.get_cmake_dir())"
if (-not $pb) { throw "pybind11.get_cmake_dir() lieferte keinen Pfad" }
Write-Host "[INFO] pybind11_DIR=$pb"

# Generator wählen
$generator = 'Ninja'
if (-not (Get-Command ninja -ErrorAction SilentlyContinue)) {
	$generator = 'Visual Studio 17 2022'
}
Write-Host "[INFO] CMake Generator: $generator"

# Configure
Write-Host "[STEP] cmake configure"
& cmake -S $src -B $build -G $generator -Dpybind11_DIR="$pb" -DCMAKE_BUILD_TYPE=$Config | Out-Host

# Build
Write-Host "[STEP] cmake build"
if ($generator -eq 'Ninja') {
	& cmake --build $build | Out-Host
} else {
	& cmake --build $build --config $Config | Out-Host
}

Write-Host "[INFO] Build-Ausgabe (.pyd/.so):"
Get-ChildItem -Recurse -Path $build -Include *.pyd,*.so -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName } | Out-Host

Write-Host "[Done] Build abgeschlossen (ohne Installation)."
