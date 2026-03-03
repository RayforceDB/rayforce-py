$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Ensure MSYS2/MinGW and Git for Windows are on PATH
$env:PATH = "C:\msys64\mingw64\bin;C:\msys64\usr\bin;C:\Program Files\Git\cmd;$env:PATH"

$EXEC_DIR = Get-Location
$RAYFORCE_GITHUB = if ($env:RAYFORCE_GITHUB) { $env:RAYFORCE_GITHUB } else { "https://github.com/RayforceDB/rayforce.git" }

$PYTHON_BIN = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { "python" }
$PYTHON_VERSION = & $PYTHON_BIN --version 2>&1 | ForEach-Object { $_.ToString().Split(" ")[1] }

Write-Host "Python version: $PYTHON_VERSION"
Write-Host "Using rayforce repo: $RAYFORCE_GITHUB"

# --- Clean previous build artifacts ---
Write-Host "Cleaning previous build artifacts..."
$cleanPaths = @(
    "$EXEC_DIR\tmp\rayforce-c",
    "$EXEC_DIR\rayforce\rayforce",
    "$EXEC_DIR\rayforce\bin",
    "$EXEC_DIR\rayforce\_rayforce_c.pyd",
    "$EXEC_DIR\rayforce\_rayforce_c.so",
    "$EXEC_DIR\rayforce\rayforce.dll",
    "$EXEC_DIR\build"
)
foreach ($p in $cleanPaths) {
    if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}
Get-ChildItem -Path $EXEC_DIR -Filter "*.egg-info" -Directory -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path $EXEC_DIR -Filter "__pycache__" -Directory -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
# Clean plugin DLLs
Get-ChildItem -Path "$EXEC_DIR\rayforce\plugins" -Filter "libraykx.*" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path "$EXEC_DIR\rayforce\plugins" -Filter "raykx.*" -ErrorAction SilentlyContinue | Remove-Item -Force

# --- Clone rayforce repo ---
Write-Host "Cloning rayforce repo from GitHub..."
git clone $RAYFORCE_GITHUB "$EXEC_DIR\tmp\rayforce-c"
Copy-Item -Recurse "$EXEC_DIR\tmp\rayforce-c\core" "$EXEC_DIR\rayforce\rayforce"

# --- Get Python build info ---
$PYTHON_INCLUDE = & $PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('INCLUDEPY'))"
$PYTHON_PYVER = & $PYTHON_BIN -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')"
$PYTHON_LIB_DIR = & $PYTHON_BIN -c "import sysconfig, os; print(os.path.dirname(sysconfig.get_config_var('INCLUDEPY'))+'\\libs')"

Write-Host "Python include: $PYTHON_INCLUDE"
Write-Host "Python version tag: $PYTHON_PYVER"
Write-Host "Python lib dir: $PYTHON_LIB_DIR"

# --- Patch Makefile for Python target ---
Write-Host "Patching Makefile for Python support..."
$pythonTarget = @"

PY_OBJECTS = core/rayforce_c.o core/raypy_init_from_py.o core/raypy_init_from_buffer.o core/raypy_read_from_rf.o core/raypy_queries.o core/raypy_io.o core/raypy_binary.o core/raypy_dynlib.o core/raypy_eval.o core/raypy_iter.o core/raypy_serde.o
PY_APP_OBJECTS = app/term.o
python: CFLAGS = `$(RELEASE_CFLAGS) -DPY_SSIZE_T_CLEAN -I$PYTHON_INCLUDE -Wno-macro-redefined
python: LDFLAGS = `$(RELEASE_LDFLAGS) -L$PYTHON_LIB_DIR -lpython$PYTHON_PYVER
python: `$(CORE_OBJECTS) `$(PY_OBJECTS) `$(PY_APP_OBJECTS)
	`$(CC) -shared -o _rayforce_c.pyd `$(CFLAGS) `$(CORE_OBJECTS) `$(PY_OBJECTS) `$(PY_APP_OBJECTS) `$(LIBS) `$(LDFLAGS)
"@
Add-Content -Path "$EXEC_DIR\tmp\rayforce-c\Makefile" -Value $pythonTarget

# --- Copy C API source files ---
Write-Host "Copying C API source files..."
$capiFiles = @(
    "rayforce_c.c", "rayforce_c.h",
    "raypy_init_from_py.c", "raypy_init_from_buffer.c", "raypy_read_from_rf.c",
    "raypy_queries.c", "raypy_io.c", "raypy_binary.c",
    "raypy_dynlib.c", "raypy_eval.c", "raypy_iter.c", "raypy_serde.c"
)
foreach ($f in $capiFiles) {
    Copy-Item "$EXEC_DIR\rayforce\capi\$f" "$EXEC_DIR\tmp\rayforce-c\core\$f"
}

# --- Build Python extension ---
Write-Host "Building Rayforce Python extension..."
Push-Location "$EXEC_DIR\tmp\rayforce-c"
C:\msys64\usr\bin\make.exe python
Pop-Location
Copy-Item "$EXEC_DIR\tmp\rayforce-c\_rayforce_c.pyd" "$EXEC_DIR\rayforce\_rayforce_c.pyd"

# --- Build Raykx plugin ---
Write-Host "Building Raykx plugin..."
Push-Location "$EXEC_DIR\tmp\rayforce-c\ext\raykx"
C:\msys64\usr\bin\make.exe release
Pop-Location
Copy-Item "$EXEC_DIR\tmp\rayforce-c\ext\raykx\raykx.dll" "$EXEC_DIR\rayforce\plugins\raykx.dll"

# --- Build Rayforce executable ---
Write-Host "Building Rayforce executable..."
Push-Location "$EXEC_DIR\tmp\rayforce-c"
C:\msys64\usr\bin\make.exe release
Pop-Location
New-Item -ItemType Directory -Force -Path "$EXEC_DIR\rayforce\bin" | Out-Null
Copy-Item "$EXEC_DIR\tmp\rayforce-c\rayforce.exe" "$EXEC_DIR\rayforce\bin\rayforce.exe"

Write-Host "Build preparation complete!"
