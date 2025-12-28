#!/bin/bash
set -e -x

EXEC_DIR=$(pwd)
RAYFORCE_GITHUB="${RAYFORCE_GITHUB:-https://github.com/RayforceDB/rayforce.git}"

PYTHON_BIN="${PYTHON_BIN:-python}"
PYTHON_VERSION=$($PYTHON_BIN --version 2>&1 | awk '{print $2}')

echo "Cleaning previous build artifacts..."
rm -rf "${EXEC_DIR}/tmp/rayforce-c"
rm -rf "${EXEC_DIR}/rayforce/rayforce"
rm -rf "${EXEC_DIR}/rayforce/bin"
rm -rf "${EXEC_DIR}/rayforce/_rayforce_c.so"
rm -rf "${EXEC_DIR}/rayforce/plugins/libraykx".*
rm -rf "${EXEC_DIR}/build"
find "${EXEC_DIR}" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "${EXEC_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "Cloning rayforce repo from GitHub..."
git clone "${RAYFORCE_GITHUB}" "${EXEC_DIR}/tmp/rayforce-c"
cp -r "${EXEC_DIR}/tmp/rayforce-c/core" "${EXEC_DIR}/rayforce/rayforce"

UNAME_S=$(uname -s)
PYTHON_INCLUDE=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('INCLUDEPY'))")
PYTHON_PYVER=$($PYTHON_BIN -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

if [[ "$UNAME_S" == "Darwin" ]]; then
    LIB_EXT="dylib"
    PYTHON_LDFLAGS=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('LDFLAGS') or '')")
    SHARED_FLAGS="-undefined dynamic_lookup"
else
    LIB_EXT="so"
    PYTHON_LDFLAGS=""
    SHARED_FLAGS=""
fi

echo "Patching Makefile for Python support..."
cat >> "${EXEC_DIR}/tmp/rayforce-c/Makefile" << EOF

PY_OBJECTS = core/rayforce_c.o core/raypy_conversion.o core/raypy_constructors.o core/raypy_readers.o core/raypy_operations.o core/raypy_queries.o core/raypy_io.o
PY_APP_OBJECTS = app/term.o
python: CFLAGS = \$(RELEASE_CFLAGS) -DPY_SSIZE_T_CLEAN -I${PYTHON_INCLUDE} -Wno-macro-redefined
python: LDFLAGS = \$(RELEASE_LDFLAGS) ${PYTHON_LDFLAGS}
python: \$(CORE_OBJECTS) \$(PY_OBJECTS) \$(PY_APP_OBJECTS)
	\$(CC) -shared -o _rayforce.so \$(CFLAGS) \$(CORE_OBJECTS) \$(PY_OBJECTS) \$(PY_APP_OBJECTS) \$(LIBS) \$(LDFLAGS) ${SHARED_FLAGS}
EOF

echo "Building Rayforce..."
cp "${EXEC_DIR}/rayforce/capi/rayforce_c.c" "${EXEC_DIR}/tmp/rayforce-c/core/rayforce_c.c"
cp "${EXEC_DIR}/rayforce/capi/rayforce_c.h" "${EXEC_DIR}/tmp/rayforce-c/core/rayforce_c.h"
cp "${EXEC_DIR}/rayforce/capi/raypy_conversion.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_conversion.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_constructors.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_constructors.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_readers.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_readers.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_operations.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_operations.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_queries.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_queries.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_io.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_io.c"

cd "${EXEC_DIR}/tmp/rayforce-c"
make python
cp "${EXEC_DIR}/tmp/rayforce-c/_rayforce.so" "${EXEC_DIR}/rayforce/_rayforce_c.so"

echo "Building Raykx..."
cd "${EXEC_DIR}/tmp/rayforce-c/ext/raykx"
make release
cp "${EXEC_DIR}/tmp/rayforce-c/ext/raykx/libraykx.${LIB_EXT}" "${EXEC_DIR}/rayforce/plugins/libraykx.${LIB_EXT}"

echo "Building Rayforce executable..."
cd "${EXEC_DIR}/tmp/rayforce-c"
make release
mkdir -p "${EXEC_DIR}/rayforce/bin"
cp "${EXEC_DIR}/tmp/rayforce-c/rayforce" "${EXEC_DIR}/rayforce/bin/rayforce"
chmod +x "${EXEC_DIR}/rayforce/bin/rayforce"

echo "Build preparation complete!"
